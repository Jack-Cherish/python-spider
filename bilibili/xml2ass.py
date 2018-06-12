# The original author of this program, Danmaku2ASS, is StarBrilliant.
# This file is released under General Public License version 3.
# You should have received a copy of General Public License text alongside with
# this program. If not, you can obtain it at http://gnu.org/copyleft/gpl.html .
# This program comes with no warranty, the author will not be resopnsible for
# any damage or problems caused by this program.

import argparse
import calendar
import gettext
import io
import json
import logging
import math
import os
import random
import re
import sys
import time
import xml.dom.minidom


if sys.version_info < (3,):
    raise RuntimeError('at least Python 3.0 is required')

gettext.install('danmaku2ass', os.path.join(os.path.dirname(os.path.abspath(os.path.realpath(sys.argv[0] or 'locale'))), 'locale'))

def SeekZero(function):
    def decorated_function(file_):
        file_.seek(0)
        try:
            return function(file_)
        finally:
            file_.seek(0)
    return decorated_function


def EOFAsNone(function):
    def decorated_function(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except EOFError:
            return None
    return decorated_function


@SeekZero
@EOFAsNone
def ProbeCommentFormat(f):
    tmp = f.read(1)
    if tmp == '[':
        return 'Acfun'
        # It is unwise to wrap a JSON object in an array!
        # See this: http://haacked.com/archive/2008/11/20/anatomy-of-a-subtle-json-vulnerability.aspx/
        # Do never follow what Acfun developers did!
    elif tmp == '{':
        tmp = f.read(14)
        if tmp == '"status_code":':
            return 'Tudou'
        elif tmp == '"root":{"total':
            return 'sH5V'
    elif tmp == '<':
        tmp = f.read(1)
        if tmp == '?':
            tmp = f.read(38)
            if tmp == 'xml version="1.0" encoding="UTF-8"?><p':
                return 'Niconico'
            elif tmp == 'xml version="1.0" encoding="UTF-8"?><i':
                return 'Bilibili'
            elif tmp == 'xml version="1.0" encoding="utf-8"?><i':
                return 'Bilibili'  # tucao.cc, with the same file format as Bilibili
            elif tmp == 'xml version="1.0" encoding="Utf-8"?>\n<':
                return 'Bilibili'  # Komica, with the same file format as Bilibili
            elif tmp == 'xml version="1.0" encoding="UTF-8"?>\n<':
                return 'MioMio'
        elif tmp == 'p':
            return 'Niconico'  # Himawari Douga, with the same file format as Niconico Douga


#
# ReadComments**** protocol
#
# Input:
#     f:         Input file
#     fontsize:  Default font size
#
# Output:
#     yield a tuple:
#         (timeline, timestamp, no, comment, pos, color, size, height, width)
#     timeline:  The position when the comment is replayed
#     timestamp: The UNIX timestamp when the comment is submitted
#     no:        A sequence of 1, 2, 3, ..., used for sorting
#     comment:   The content of the comment
#     pos:       0 for regular moving comment,
#                1 for bottom centered comment,
#                2 for top centered comment,
#                3 for reversed moving comment
#     color:     Font color represented in 0xRRGGBB,
#                e.g. 0xffffff for white
#     size:      Font size
#     height:    The estimated height in pixels
#                i.e. (comment.count('\n')+1)*size
#     width:     The estimated width in pixels
#                i.e. CalculateLength(comment)*size
#
# After implementing ReadComments****, make sure to update ProbeCommentFormat
# and CommentFormatMap.
#


def ReadCommentsNiconico(f, fontsize):
    NiconicoColorMap = {'red': 0xff0000, 'pink': 0xff8080, 'orange': 0xffcc00, 'yellow': 0xffff00, 'green': 0x00ff00, 'cyan': 0x00ffff, 'blue': 0x0000ff, 'purple': 0xc000ff, 'black': 0x000000, 'niconicowhite': 0xcccc99, 'white2': 0xcccc99, 'truered': 0xcc0033, 'red2': 0xcc0033, 'passionorange': 0xff6600, 'orange2': 0xff6600, 'madyellow': 0x999900, 'yellow2': 0x999900, 'elementalgreen': 0x00cc66, 'green2': 0x00cc66, 'marineblue': 0x33ffcc, 'blue2': 0x33ffcc, 'nobleviolet': 0x6633cc, 'purple2': 0x6633cc}
    dom = xml.dom.minidom.parse(f)
    comment_element = dom.getElementsByTagName('chat')
    for comment in comment_element:
        try:
            c = str(comment.childNodes[0].wholeText)
            if c.startswith('/'):
                continue  # ignore advanced comments
            pos = 0
            color = 0xffffff
            size = fontsize
            for mailstyle in str(comment.getAttribute('mail')).split():
                if mailstyle == 'ue':
                    pos = 1
                elif mailstyle == 'shita':
                    pos = 2
                elif mailstyle == 'big':
                    size = fontsize*1.44
                elif mailstyle == 'small':
                    size = fontsize*0.64
                elif mailstyle in NiconicoColorMap:
                    color = NiconicoColorMap[mailstyle]
            yield (max(int(comment.getAttribute('vpos')), 0)*0.01, int(comment.getAttribute('date')), int(comment.getAttribute('no')), c, pos, color, size, (c.count('\n')+1)*size, CalculateLength(c)*size)
        except (AssertionError, AttributeError, IndexError, TypeError, ValueError):
            logging.warning(_('Invalid comment: %s') % comment.toxml())
            continue


def ReadCommentsAcfun(f, fontsize):
    comment_element = json.load(f)
    for i, comment in enumerate(comment_element):
        try:
            p = str(comment['c']).split(',')
            assert len(p) >= 6
            assert p[2] in ('1', '2', '4', '5', '7')
            size = int(p[3])*fontsize/25.0
            if p[2] != '7':
                c = str(comment['m']).replace('\\r', '\n').replace('\r', '\n')
                yield (float(p[0]), int(p[5]), i, c, {'1': 0, '2': 0, '4': 2, '5': 1}[p[2]], int(p[1]), size, (c.count('\n')+1)*size, CalculateLength(c)*size)
            else:
                c = dict(json.loads(comment['m']))
                yield (float(p[0]), int(p[5]), i, c, 'acfunpos', int(p[1]), size, 0, 0)
        except (AssertionError, AttributeError, IndexError, TypeError, ValueError):
            logging.warning(_('Invalid comment: %r') % comment)
            continue


def ReadCommentsBilibili(f, fontsize):
    dom = xml.dom.minidom.parse(f)
    comment_element = dom.getElementsByTagName('d')
    for i, comment in enumerate(comment_element):
        try:
            p = str(comment.getAttribute('p')).split(',')
            assert len(p) >= 5
            assert p[1] in ('1', '4', '5', '6', '7')
            if p[1] != '7':
                c = str(comment.childNodes[0].wholeText).replace('/n', '\n')
                size = int(p[2])*fontsize/25.0
                yield (float(p[0]), int(p[4]), i, c, {'1': 0, '4': 2, '5': 1, '6': 3}[p[1]], int(p[3]), size, (c.count('\n')+1)*size, CalculateLength(c)*size)
            else:  # positioned comment
                c = str(comment.childNodes[0].wholeText)
                yield (float(p[0]), int(p[4]), i, c, 'bilipos', int(p[3]), int(p[2]), 0, 0)
        except (AssertionError, AttributeError, IndexError, TypeError, ValueError):
            logging.warning(_('Invalid comment: %s') % comment.toxml())
            continue


def ReadCommentsTudou(f, fontsize):
    comment_element = json.load(f)
    for i, comment in enumerate(comment_element['comment_list']):
        try:
            assert comment['pos'] in (3, 4, 6)
            c = str(comment['data'])
            assert comment['size'] in (0, 1, 2)
            size = {0: 0.64, 1: 1, 2: 1.44}[comment['size']]*fontsize
            yield (int(comment['replay_time']*0.001), int(comment['commit_time']), i, c, {3: 0, 4: 2, 6: 1}[comment['pos']], int(comment['color']), size, (c.count('\n')+1)*size, CalculateLength(c)*size)
        except (AssertionError, AttributeError, IndexError, TypeError, ValueError):
            logging.warning(_('Invalid comment: %r') % comment)
            continue


def ReadCommentsMioMio(f, fontsize):
    NiconicoColorMap = {'red': 0xff0000, 'pink': 0xff8080, 'orange': 0xffc000, 'yellow': 0xffff00, 'green': 0x00ff00, 'cyan': 0x00ffff, 'blue': 0x0000ff, 'purple': 0xc000ff, 'black': 0x000000}
    dom = xml.dom.minidom.parse(f)
    comment_element = dom.getElementsByTagName('data')
    for i, comment in enumerate(comment_element):
        try:
            message = comment.getElementsByTagName('message')[0]
            c = str(message.childNodes[0].wholeText)
            pos = 0
            size = int(message.getAttribute('fontsize'))*fontsize/25.0
            yield (float(comment.getElementsByTagName('playTime')[0].childNodes[0].wholeText), int(calendar.timegm(time.strptime(comment.getElementsByTagName('times')[0].childNodes[0].wholeText, '%Y-%m-%d %H:%M:%S')))-28800, i, c, {'1': 0, '4': 2, '5': 1}[message.getAttribute('mode')], int(message.getAttribute('color')), size, (c.count('\n')+1)*size, CalculateLength(c)*size)
        except (AssertionError, AttributeError, IndexError, TypeError, ValueError):
            logging.warning(_('Invalid comment: %s') % comment.toxml())
            continue


def ReadCommentsSH5V(f, fontsize):
    comment_element = json.load(f)
    for i, comment in enumerate(comment_element["root"]["bgs"]):
        try:
            c_at = str(comment['at'])
            c_type = str(comment['type'])
            c_date = str(comment['timestamp'])
            c_color = str(comment['color'])
            c = str(comment['text'])
            size = fontsize
            if c_type != '7':
                yield (float(c_at), int(c_date), i, c, {'0': 0, '1': 0, '4': 2, '5': 1}[c_type], int(c_color[1:], 16), size, (c.count('\n')+1)*size, CalculateLength(c)*size)
            else:
                c_x = float(comment['x'])
                c_y = float(comment['y'])
                size = int(comment['size'])
                dur = int(comment['dur'])
                data1 = float(comment['data1'])
                data2 = float(comment['data2'])
                data3 = int(comment['data3'])
                data4 = int(comment['data4'])
                yield (float(c_at), int(c_date), i, c, 'sH5Vpos', int(c_color[1:], 16), size, 0, 0, c_x, c_y, dur, data1, data2, data3, data4)
        except (AssertionError, AttributeError, IndexError, TypeError, ValueError):
            logging.warning(_('Invalid comment: %r') % comment)
            continue


CommentFormatMap = {None: None, 'Niconico': ReadCommentsNiconico, 'Acfun': ReadCommentsAcfun, 'Bilibili': ReadCommentsBilibili, 'Tudou': ReadCommentsTudou, 'MioMio': ReadCommentsMioMio, 'sH5V': ReadCommentsSH5V}


def WriteCommentBilibiliPositioned(f, c, width, height, styleid):
    #BiliPlayerSize = (512, 384)  # Bilibili player version 2010
    #BiliPlayerSize = (540, 384)  # Bilibili player version 2012
    BiliPlayerSize = (672, 438)  # Bilibili player version 2014
    ZoomFactor = GetZoomFactor(BiliPlayerSize, (width, height))

    def GetPosition(InputPos, isHeight):
        isHeight = int(isHeight)  # True -> 1
        if isinstance(InputPos, int):
            return ZoomFactor[0]*InputPos+ZoomFactor[isHeight+1]
        elif isinstance(InputPos, float):
            if InputPos > 1:
                return ZoomFactor[0]*InputPos+ZoomFactor[isHeight+1]
            else:
                return BiliPlayerSize[isHeight]*ZoomFactor[0]*InputPos+ZoomFactor[isHeight+1]
        else:
            try:
                InputPos = int(InputPos)
            except ValueError:
                InputPos = float(InputPos)
            return GetPosition(InputPos, isHeight)

    try:
        comment_args = safe_list(json.loads(c[3]))
        text = ASSEscape(str(comment_args[4]).replace('/n', '\n'))
        from_x = comment_args.get(0, 0)
        from_y = comment_args.get(1, 0)
        to_x = comment_args.get(7, from_x)
        to_y = comment_args.get(8, from_y)
        from_x = round(GetPosition(from_x, False))
        from_y = round(GetPosition(from_y, True))
        to_x = round(GetPosition(to_x, False))
        to_y = round(GetPosition(to_y, True))
        alpha = safe_list(str(comment_args.get(2, '1')).split('-'))
        from_alpha = float(alpha.get(0, 1))
        to_alpha = float(alpha.get(1, from_alpha))
        from_alpha = 255-round(from_alpha*255)
        to_alpha = 255-round(to_alpha*255)
        rotate_z = int(comment_args.get(5, 0))
        rotate_y = int(comment_args.get(6, 0))
        lifetime = float(comment_args.get(3, 4500))
        duration = int(comment_args.get(9, lifetime*1000))
        delay = int(comment_args.get(10, 0))
        fontface = comment_args.get(12)
        isborder = comment_args.get(11, 'true')
        styles = []
        if (from_x, from_y) == (to_x, to_y):
            styles.append('\\pos(%s, %s)' % (from_x, from_y))
        else:
            styles.append('\\move(%s, %s, %s, %s, %s, %s)' % (from_x, from_y, to_x, to_y, delay, delay+duration))
        styles.append('\\frx%s\\fry%s\\frz%s\\fax%s\\fay%s' % ConvertFlashRotation(rotate_y, rotate_z, (from_x-ZoomFactor[1])/(width-ZoomFactor[1]*2), (from_y-ZoomFactor[2])/(height-ZoomFactor[2]*2)))
        if (from_x, from_y) != (to_x, to_y):
            styles.append('\\t(%s, %s, ' % (delay, delay+duration))
            styles.append('\\frx%s\\fry%s\\frz%s\\fax%s\\fay%s' % ConvertFlashRotation(rotate_y, rotate_z, (to_x-ZoomFactor[1])/(width-ZoomFactor[1]*2), (to_y-ZoomFactor[2])/(height-ZoomFactor[2]*2)))
            styles.append(')')
        if fontface:
            styles.append('\\fn%s' % ASSEscape(fontface))
        styles.append('\\fs%s' % round(c[6]*ZoomFactor[0]))
        if c[5] != 0xffffff:
            styles.append('\\c&H%02X%02X%02X&' % (c[5] & 0xff, (c[5] >> 8) & 0xff, (c[5] >> 16) & 0xff))
            if c[5] == 0x000000:
                styles.append('\\3c&HFFFFFF&')
        if from_alpha == to_alpha:
            styles.append('\\alpha&H%02X' % from_alpha)
        elif (from_alpha, to_alpha) == (255, 0):
            styles.append('\\fad(%s,0)' % (lifetime*1000))
        elif (from_alpha, to_alpha) == (0, 255):
            styles.append('\\fad(0, %s)' % (lifetime*1000))
        else:
            styles.append('\\fade(%(from_alpha)s, %(to_alpha)s, %(to_alpha)s, 0, %(end_time)s, %(end_time)s, %(end_time)s)' % {'from_alpha': from_alpha, 'to_alpha': to_alpha, 'end_time': lifetime*1000})
        if isborder == 'false':
            styles.append('\\bord0')
        f.write('Dialogue: -1,%(start)s,%(end)s,%(styleid)s,,0,0,0,,{%(styles)s}%(text)s\n' % {'start': ConvertTimestamp(c[0]), 'end': ConvertTimestamp(c[0]+lifetime), 'styles': ''.join(styles), 'text': text, 'styleid': styleid})
    except (IndexError, ValueError) as e:
        try:
            logging.warning(_('Invalid comment: %r') % c[3])
        except IndexError:
            logging.warning(_('Invalid comment: %r') % c)


def WriteCommentAcfunPositioned(f, c, width, height, styleid):
    AcfunPlayerSize = (560, 400)
    ZoomFactor = GetZoomFactor(AcfunPlayerSize, (width, height))

    def GetPosition(InputPos, isHeight):
        isHeight = int(isHeight)  # True -> 1
        return AcfunPlayerSize[isHeight]*ZoomFactor[0]*InputPos*0.001+ZoomFactor[isHeight+1]

    def GetTransformStyles(x=None, y=None, scale_x=None, scale_y=None, rotate_z=None, rotate_y=None, color=None, alpha=None):
        styles = []
        if x is not None and y is not None:
            styles.append('\\pos(%s, %s)' % (x, y))
        if scale_x is not None:
            styles.append('\\fscx%s' % scale_x)
        if scale_y is not None:
            styles.append('\\fscy%s' % scale_y)
        if rotate_z is not None and rotate_y is not None:
            assert x is not None
            assert y is not None
            styles.append('\\frx%s\\fry%s\\frz%s\\fax%s\\fay%s' % ConvertFlashRotation(rotate_y, rotate_z, (x-ZoomFactor[1])/(width-ZoomFactor[1]*2), (y-ZoomFactor[2])/(height-ZoomFactor[2]*2)))
        if color is not None:
            styles.append('\\c&H%02X%02X%02X&' % (color & 0xff, (color >> 8) & 0xff, (color >> 16) & 0xff))
            if color == 0x000000:
                styles.append('\\3c&HFFFFFF&')
        if alpha is not None:
            alpha = 255-round(alpha*255)
            styles.append('\\alpha&H%02X' % alpha)
        return styles

    def FlushCommentLine(f, text, styles, start_time, end_time, styleid):
        if end_time > start_time:
            f.write('Dialogue: -1,%(start)s,%(end)s,%(styleid)s,,0,0,0,,{%(styles)s}%(text)s\n' % {'start': ConvertTimestamp(start_time), 'end': ConvertTimestamp(end_time), 'styles': ''.join(styles), 'text': text, 'styleid': styleid})

    try:
        comment_args = c[3]
        text = ASSEscape(str(comment_args['n']).replace('\r', '\n').replace('\r', '\n'))
        common_styles = []
        anchor = {0: 7, 1: 8, 2: 9, 3: 4, 4: 5, 5: 6, 6: 1, 7: 2, 8: 3}.get(comment_args.get('c', 0), 7)
        if anchor != 7:
            common_styles.append('\\an%s' % anchor)
        font = comment_args.get('w')
        if font:
            font = dict(font)
            fontface = font.get('f')
            if fontface:
                common_styles.append('\\fn%s' % ASSEscape(str(fontface)))
            fontbold = bool(font.get('b'))
            if fontbold:
                common_styles.append('\\b1')
        common_styles.append('\\fs%s' % round(c[6]*ZoomFactor[0]))
        isborder = bool(comment_args.get('b', True))
        if not isborder:
            common_styles.append('\\bord0')
        to_pos = dict(comment_args.get('p', {'x': 0, 'y': 0}))
        to_x = round(GetPosition(int(to_pos.get('x', 0)), False))
        to_y = round(GetPosition(int(to_pos.get('y', 0)), True))
        to_scale_x = round(float(comment_args.get('e', 1.0))*100)
        to_scale_y = round(float(comment_args.get('f', 1.0))*100)
        to_rotate_z = float(comment_args.get('r', 0.0))
        to_rotate_y = float(comment_args.get('k', 0.0))
        to_color = c[5]
        to_alpha = float(comment_args.get('a', 1.0))
        from_time = float(comment_args.get('t', 0.0))
        action_time = float(comment_args.get('l', 3.0))
        actions = list(comment_args.get('z', []))
        transform_styles = GetTransformStyles(to_x, to_y, to_scale_x, to_scale_y, to_rotate_z, to_rotate_y, to_color, to_alpha)
        FlushCommentLine(f, text, common_styles+transform_styles, c[0]+from_time, c[0]+from_time+action_time, styleid)
        for action in actions:
            action = dict(action)
            from_x, from_y = to_x, to_y
            from_scale_x, from_scale_y = to_scale_x, to_scale_y
            from_rotate_z, from_rotate_y = to_rotate_z, to_rotate_y
            from_color, from_alpha = to_color, to_alpha
            from_time += action_time
            action_time = float(action.get('l', 0.0))
            action_styles = []
            if 'x' in action:
                to_x = round(GetPosition(int(action['x']), False))
            if 'y' in action:
                to_y = round(GetPosition(int(action['y']), True))
            if 'f' in action:
                to_scale_x = round(float(action['f'])*100)
                action_styles.append('\\fscx%s' % to_scale_x)
            if 'g' in action:
                to_scale_y = round(float(action['g'])*100)
                action_styles.append('\\fscy%s' % to_scale_y)
            if 'c' in action:
                to_color = int(action['c'])
                action_styles.append('\\c&H%02X%02X%02X&' % (to_color & 0xff, (to_color >> 8) & 0xff, (to_color >> 16) & 0xff))
            if 't' in action:
                to_alpha = float(action['t'])
                action_styles.append('\\alpha&H%02X' % (255-round(to_alpha*255)))
            if 'd' in action:
                to_rotate_z = float(action['d'])
            if 'e' in action:
                to_rotate_y = float(action['e'])
            if ('x' in action) or ('y' in action):
                transform_styles = GetTransformStyles(None, None, from_scale_x, from_scale_y, None, None, from_color, from_alpha)
                transform_styles.append('\\move(%s, %s, %s, %s)' % (from_x, from_y, to_x, to_y))
                action_styles.append('\\frx%s\\fry%s\\frz%s\\fax%s\\fay%s' % ConvertFlashRotation(to_rotate_y, to_rotate_z, (to_x-ZoomFactor[1])/(width-ZoomFactor[1]*2), (to_y-ZoomFactor[2])/(width-ZoomFactor[2]*2)))
            elif ('d' in action) or ('e' in action):
                action_styles.append('\\frx%s\\fry%s\\frz%s\\fax%s\\fay%s' % ConvertFlashRotation(to_rotate_y, to_rotate_z, (to_x-ZoomFactor[1])/(width-ZoomFactor[1]*2), (to_y-ZoomFactor[2])/(width-ZoomFactor[2]*2)))
            else:
                transform_styles = GetTransformStyles(from_x, from_y, from_scale_x, from_scale_y, from_rotate_z, from_rotate_y, from_color, from_alpha)
            if action_styles:
                transform_styles.append('\\t(%s)' % (''.join(action_styles)))
            FlushCommentLine(f, text, common_styles+transform_styles, c[0]+from_time, c[0]+from_time+action_time, styleid)
    except (IndexError, ValueError) as e:
        logging.warning(_('Invalid comment: %r') % c[3])


def WriteCommentSH5VPositioned(f, c, width, height, styleid):

    def GetTransformStyles(x=None, y=None, fsize=None, rotate_z=None, rotate_y=None, color=None, alpha=None):
        styles = []
        if x is not None and y is not None:
            styles.append('\\pos(%s, %s)' % (x, y))
        if fsize is not None:
            styles.append('\\fs%s' % fsize)
        if rotate_y is not None and rotate_z is not None:
            styles.append('\\frz%s' % round(rotate_z))
            styles.append('\\fry%s' % round(rotate_y))
        if color is not None:
            styles.append('\\c&H%02X%02X%02X&' % (color & 0xff, (color >> 8) & 0xff, (color >> 16) & 0xff))
            if color == 0x000000:
                styles.append('\\3c&HFFFFFF&')
        if alpha is not None:
            alpha = 255-round(alpha*255)
            styles.append('\\alpha&H%02X' % alpha)
        return styles

    def FlushCommentLine(f, text, styles, start_time, end_time, styleid):
        if end_time > start_time:
            f.write('Dialogue: -1,%(start)s,%(end)s,%(styleid)s,,0,0,0,,{%(styles)s}%(text)s\n' % {'start': ConvertTimestamp(start_time), 'end': ConvertTimestamp(end_time), 'styles': ''.join(styles), 'text': text, 'styleid': styleid})

    try:
        text = ASSEscape(str(c[3]))
        to_x = round(float(c[9])*width)
        to_y = round(float(c[10])*height)
        to_rotate_z = -int(c[14])
        to_rotate_y = -int(c[15])
        to_color = c[5]
        to_alpha = float(c[12])
        #Note: Alpha transition hasn't been worked out yet.
        to_size = round(int(c[6])*math.sqrt(width*height/307200))
        #Note: Because sH5V's data is the absolute size of font,temporarily solve by it at present.[*math.sqrt(width/640*height/480)]
        #But it seems to be working fine...
        from_time = float(c[0])
        action_time = float(c[11])/1000
        transform_styles = GetTransformStyles(to_x, to_y, to_size, to_rotate_z, to_rotate_y, to_color, to_alpha)
        FlushCommentLine(f, text, transform_styles, from_time, from_time+action_time, styleid)
    except (IndexError, ValueError) as e:
        logging.warning(_('Invalid comment: %r') % c[3])


# Result: (f, dx, dy)
# To convert: NewX = f*x+dx, NewY = f*y+dy
def GetZoomFactor(SourceSize, TargetSize):
    try:
        if (SourceSize, TargetSize) == GetZoomFactor.Cached_Size:
            return GetZoomFactor.Cached_Result
    except AttributeError:
        pass
    GetZoomFactor.Cached_Size = (SourceSize, TargetSize)
    try:
        SourceAspect = SourceSize[0]/SourceSize[1]
        TargetAspect = TargetSize[0]/TargetSize[1]
        if TargetAspect < SourceAspect:  # narrower
            ScaleFactor = TargetSize[0]/SourceSize[0]
            GetZoomFactor.Cached_Result = (ScaleFactor, 0, (TargetSize[1]-TargetSize[0]/SourceAspect)/2)
        elif TargetAspect > SourceAspect:  # wider
            ScaleFactor = TargetSize[1]/SourceSize[1]
            GetZoomFactor.Cached_Result = (ScaleFactor, (TargetSize[0]-TargetSize[1]*SourceAspect)/2, 0)
        else:
            GetZoomFactor.Cached_Result = (TargetSize[0]/SourceSize[0], 0, 0)
        return GetZoomFactor.Cached_Result
    except ZeroDivisionError:
        GetZoomFactor.Cached_Result = (1, 0, 0)
        return GetZoomFactor.Cached_Result


# Calculation is based on https://github.com/jabbany/CommentCoreLibrary/issues/5#issuecomment-40087282
#                     and https://github.com/m13253/danmaku2ass/issues/7#issuecomment-41489422
# Input: X relative horizonal coordinate: 0 for left edge, 1 for right edge.
#        Y relative vertical coordinate: 0 for top edge, 1 for bottom edge.
# FOV = 1.0/math.tan(100*math.pi/360.0)
# Result: (rotX, rotY, rotZ, shearX, shearY)
def ConvertFlashRotation(rotY, rotZ, X, Y, FOV=math.tan(2*math.pi/9.0)):
    def WrapAngle(deg):
        return 180-((180-deg)%360)
    def CalcPerspectiveCorrection(alpha, X, FOV=FOV):
        alpha = WrapAngle(alpha)
        if FOV is None:
            return alpha
        if 0 <= alpha <= 180:
            costheta = (FOV*math.cos(alpha*math.pi/180.0)-X*math.sin(alpha*math.pi/180.0))/(FOV+max(2, abs(X)+1)*math.sin(alpha*math.pi/180.0))
            try:
                if costheta > 1:
                    costheta = 1
                    raise ValueError
                elif costheta < -1:
                    costheta = -1
                    raise ValueError
            except ValueError:
                logging.error('Clipped rotation angle: (alpha=%s, X=%s), it is a bug!' % (alpha, X))
            theta = math.acos(costheta)*180/math.pi
        else:
            costheta = (FOV*math.cos(alpha*math.pi/180.0)-X*math.sin(alpha*math.pi/180.0))/(FOV-max(2, abs(X)+1)*math.sin(alpha*math.pi/180.0))
            try:
                if costheta > 1:
                    costheta = 1
                    raise ValueError
                elif costheta < -1:
                    costheta = -1
                    raise ValueError
            except ValueError:
                logging.error('Clipped rotation angle: (alpha=%s, X=%s), it is a bug!' % (alpha, X))
            theta = -math.acos(costheta)*180/math.pi
        return WrapAngle(theta)
    X = 2*X-1
    Y = 2*Y-1
    rotY = WrapAngle(rotY)
    rotZ = WrapAngle(rotZ)
    if rotY == 0 or rotZ == 0:
        outX = 0
        outY = -rotY  # Positive value means clockwise in Flash
        outZ = -rotZ
    else:
        rotY = rotY*math.pi/180.0
        rotZ = rotZ*math.pi/180.0
        outY = math.atan2(-math.sin(rotY)*math.cos(rotZ), math.cos(rotY))*180/math.pi
        outZ = math.atan2(-math.cos(rotY)*math.sin(rotZ), math.cos(rotZ))*180/math.pi
        outX = math.asin(math.sin(rotY)*math.sin(rotZ))*180/math.pi
    if FOV is not None:
        #outX = CalcPerspectiveCorrection(outX, -Y, FOV*0.75)
        outY = CalcPerspectiveCorrection(outY, X, FOV)
    return (WrapAngle(round(outX)), WrapAngle(round(outY)), WrapAngle(round(outZ)), 0, round(-0.75*Y*math.sin(outY*math.pi/180.0), 3))


def ProcessComments(comments, f, width, height, bottomReserved, fontface, fontsize, alpha, lifetime, reduced, progress_callback):
    styleid = 'Danmaku2ASS_%04x' % random.randint(0, 0xffff)
    WriteASSHead(f, width, height, fontface, fontsize, alpha, styleid)
    rows = [[None]*(height-bottomReserved+1) for i in range(4)]
    for idx, i in enumerate(comments):
        if progress_callback and idx % 1000 == 0:
            progress_callback(idx, len(comments))
        if isinstance(i[4], int):
            row = 0
            rowmax = height-bottomReserved-i[7]
            while row <= rowmax:
                freerows = TestFreeRows(rows, i, row, width, height, bottomReserved, lifetime)
                if freerows >= i[7]:
                    MarkCommentRow(rows, i, row)
                    WriteComment(f, i, row, width, height, bottomReserved, fontsize, lifetime, styleid)
                    break
                else:
                    row += freerows or 1
            else:
                if not reduced:
                    row = FindAlternativeRow(rows, i, height, bottomReserved)
                    MarkCommentRow(rows, i, row)
                    WriteComment(f, i, row, width, height, bottomReserved, fontsize, lifetime, styleid)
        elif i[4] == 'bilipos':
            WriteCommentBilibiliPositioned(f, i, width, height, styleid)
        elif i[4] == 'acfunpos':
            WriteCommentAcfunPositioned(f, i, width, height, styleid)
        elif i[4] == 'sH5Vpos':
            WriteCommentSH5VPositioned(f, i, width, height, styleid)
        else:
            logging.warning(_('Invalid comment: %r') % i[3])
    if progress_callback:
        progress_callback(len(comments), len(comments))


def TestFreeRows(rows, c, row, width, height, bottomReserved, lifetime):
    res = 0
    rowmax = height-bottomReserved
    targetRow = None
    if c[4] in (1, 2):
        while row < rowmax and res < c[7]:
            if targetRow != rows[c[4]][row]:
                targetRow = rows[c[4]][row]
                if targetRow and targetRow[0]+lifetime > c[0]:
                    break
            row += 1
            res += 1
    else:
        try:
            thresholdTime = c[0]-lifetime*(1-width/(c[8]+width))
        except ZeroDivisionError:
            thresholdTime = c[0]-lifetime
        while row < rowmax and res < c[7]:
            if targetRow != rows[c[4]][row]:
                targetRow = rows[c[4]][row]
                try:
                    if targetRow and (targetRow[0] > thresholdTime or targetRow[0]+targetRow[8]*lifetime/(targetRow[8]+width) > c[0]):
                        break
                except ZeroDivisionError:
                    pass
            row += 1
            res += 1
    return res


def FindAlternativeRow(rows, c, height, bottomReserved):
    res = 0
    for row in range(height-bottomReserved-math.ceil(c[7])):
        if not rows[c[4]][row]:
            return row
        elif rows[c[4]][row][0] < rows[c[4]][res][0]:
            res = row
    return res


def MarkCommentRow(rows, c, row):
    try:
        for i in range(row, row+math.ceil(c[7])):
            rows[c[4]][i] = c
    except IndexError:
        pass


def WriteASSHead(f, width, height, fontface, fontsize, alpha, styleid):
    f.write(
'''
[Script Info]
; Script generated by Danmaku2ASS
; https://github.com/m13253/danmaku2ass
Script Updated By: Danmaku2ASS (https://github.com/m13253/danmaku2ass)
ScriptType: v4.00+
WrapStyle: 2
Collisions: Normal
PlayResX: %(width)s
PlayResY: %(height)s
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: %(styleid)s, %(fontface)s, %(fontsize)s, &H%(alpha)02XFFFFFF, &H%(alpha)02XFFFFFF, &H%(alpha)02X000000, &H%(alpha)02X000000, 0, 0, 0, 0, 100, 100, 0.00, 0.00, 1, %(outline)s, 0, 7, 0, 0, 0, 0
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
''' % {'width': width, 'height': height, 'fontface': fontface, 'fontsize': round(fontsize), 'alpha': 255-round(alpha*255), 'outline': round(fontsize/25), 'styleid': styleid}
    )


def WriteComment(f, c, row, width, height, bottomReserved, fontsize, lifetime, styleid):
    text = ASSEscape(c[3])
    styles = []
    if c[4] == 1:
        styles.append('\\an8\\pos(%(halfwidth)s, %(row)s)' % {'halfwidth': round(width/2), 'row': row})
    elif c[4] == 2:
        styles.append('\\an2\\pos(%(halfwidth)s, %(row)s)' % {'halfwidth': round(width/2), 'row': ConvertType2(row, height, bottomReserved)})
    elif c[4] == 3:
        styles.append('\\move(%(neglen)s, %(row)s, %(width)s, %(row)s)' % {'width': width, 'row': row, 'neglen': -math.ceil(c[8])})
    else:
        styles.append('\\move(%(width)s, %(row)s, %(neglen)s, %(row)s)' % {'width': width, 'row': row, 'neglen': -math.ceil(c[8])})
    if not (-1 < c[6]-fontsize < 1):
        styles.append('\\fs%s' % round(c[6]))
    if c[5] != 0xffffff:
        styles.append('\\c&H%02X%02X%02X&' % (c[5] & 0xff, (c[5] >> 8) & 0xff, (c[5] >> 16) & 0xff))
        if c[5] == 0x000000:
            styles.append('\\3c&HFFFFFF&')
    f.write('Dialogue: 2,%(start)s,%(end)s,%(styleid)s,,0000,0000,0000,,{%(styles)s}%(text)s\n' % {'start': ConvertTimestamp(c[0]), 'end': ConvertTimestamp(c[0]+lifetime), 'styles': ''.join(styles), 'text': text, 'styleid': styleid})


def ASSEscape(s):
    return '\\N'.join((i or ' ' for i in str(s).replace('\\', '\\\\').replace('{', '\\{').replace('}', '\\}').split('\n')))


def CalculateLength(s):
    return max(map(len, s.split('\n')))  # May not be accurate


def ConvertTimestamp(timestamp):
    timestamp = round(timestamp*100.0)
    hour, minute = divmod(timestamp, 360000)
    minute, second = divmod(minute, 6000)
    second, centsecond = divmod(second, 100)
    return '%d:%02d:%02d.%02d' % (int(hour), int(minute), int(second), int(centsecond))


def ConvertType2(row, height, bottomReserved):
    return height-bottomReserved-row


def ConvertToFile(filename_or_file, *args, **kwargs):
    if isinstance(filename_or_file, bytes):
        filename_or_file = str(bytes(filename_or_file).decode('utf-8', 'replace'))
    if isinstance(filename_or_file, str):
        return open(filename_or_file, *args, **kwargs)
    else:
        return filename_or_file


def FilterBadChars(f):
    s = f.read()
    s = re.sub('[\\x00-\\x08\\x0b\\x0c\\x0e-\\x1f]', '\ufffd', s)
    return io.StringIO(s)


class safe_list(list):
    def get(self, index, default=None):
        try:
            return self[index]
        except IndexError:
            return default


def export(func):
    global __all__
    try:
        __all__.append(func.__name__)
    except NameError:
        __all__ = [func.__name__]
    return func


@export
def Danmaku2ASS(input_files, output_file, stage_width, stage_height, reserve_blank=0, font_face=_('(FONT) sans-serif')[7:], font_size=25.0, text_opacity=1.0, comment_duration=5.0, is_reduce_comments=False, progress_callback=None):
    fo = None
    comments = ReadComments(input_files, font_size)
    try:
        if output_file:
            fo = ConvertToFile(output_file, 'w', encoding='utf-8-sig', errors='replace', newline='\r\n')
        else:
            fo = sys.stdout
        ProcessComments(comments, fo, stage_width, stage_height, reserve_blank, font_face, font_size, text_opacity, comment_duration, is_reduce_comments, progress_callback)
    finally:
        if output_file and fo != output_file:
            fo.close()


@export
def ReadComments(input_files, font_size=25.0, progress_callback=None):
    if isinstance(input_files, bytes):
        input_files = str(bytes(input_files).decode('utf-8', 'replace'))
    if isinstance(input_files, str):
        input_files = [input_files]
    else:
        input_files = list(input_files)
    comments = []
    for idx, i in enumerate(input_files):
        if progress_callback:
            progress_callback(idx, len(input_files))
        with ConvertToFile(i, 'r', encoding='utf-8', errors='replace') as f:
            CommentProcessor = GetCommentProcessor(f)
            if not CommentProcessor:
                raise ValueError(_('Unknown comment file format: %s') % i)
            comments.extend(CommentProcessor(FilterBadChars(f), font_size))
    if progress_callback:
        progress_callback(len(input_files), len(input_files))
    comments.sort()
    return comments


@export
def GetCommentProcessor(input_file):
    return CommentFormatMap[ProbeCommentFormat(input_file)]


def main():
    if len(sys.argv) == 1:
        sys.argv.append('--help')
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', metavar=_('OUTPUT'), help=_('Output file'))
    parser.add_argument('-s', '--size', metavar=_('WIDTHxHEIGHT'), required=True, help=_('Stage size in pixels'))
    parser.add_argument('-fn', '--font', metavar=_('FONT'), help=_('Specify font face [default: %s]') % _('(FONT) sans-serif')[7:], default=_('(FONT) sans-serif')[7:])
    parser.add_argument('-fs', '--fontsize', metavar=_('SIZE'), help=(_('Default font size [default: %s]') % 25), type=float, default=25.0)
    parser.add_argument('-a', '--alpha', metavar=_('ALPHA'), help=_('Text opacity'), type=float, default=1.0)
    parser.add_argument('-l', '--lifetime', metavar=_('SECONDS'), help=_('Duration of comment display [default: %s]') % 5, type=float, default=5.0)
    parser.add_argument('-p', '--protect', metavar=_('HEIGHT'), help=_('Reserve blank on the bottom of the stage'), type=int, default=0)
    parser.add_argument('-r', '--reduce', action='store_true', help=_('Reduce the amount of comments if stage is full'))
    parser.add_argument('file', metavar=_('FILE'), nargs='+', help=_('Comment file to be processed'))
    args = parser.parse_args()
    try:
        width, height = str(args.size).split('x', 1)
        width = int(width)
        height = int(height)
    except ValueError:
        raise ValueError(_('Invalid stage size: %r') % args.size)
    Danmaku2ASS(args.file, args.output, width, height, args.protect, args.font, args.fontsize, args.alpha, args.lifetime, args.reduce)


if __name__ == '__main__':
    main()
