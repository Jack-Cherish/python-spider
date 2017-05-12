#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from MyQR.myqr import run
import os

def main():
    import argparse
    argparser = argparse.ArgumentParser()
    argparser.add_argument('Words', help = 'The words to produce you QR-code picture, like a URL or a sentence. Please read the README file for the supported characters.')
    argparser.add_argument('-v', '--version', type = int, choices = range(1,41), default = 1, help = 'The version means the length of a side of the QR-Code picture. From little size to large is 1 to 40.')
    argparser.add_argument('-l', '--level', choices = list('LMQH'), default = 'H', help = 'Use this argument to choose an Error-Correction-Level: L(Low), M(Medium) or Q(Quartile), H(High). Otherwise, just use the default one: H')
    argparser.add_argument('-p', '--picture', help = 'the picture  e.g. example.jpg')
    argparser.add_argument('-c', '--colorized', action = 'store_true', help = "Produce a colorized QR-Code with your picture. Just works when there is a correct '-p' or '--picture'.")
    argparser.add_argument('-con', '--contrast', type = float, default = 1.0, help = 'A floating point value controlling the enhancement of contrast. Factor 1.0 always returns a copy of the original image, lower factors mean less color (brightness, contrast, etc), and higher values more. There are no restrictions on this value. Default: 1.0')
    argparser.add_argument('-bri', '--brightness', type = float, default = 1.0, help = 'A floating point value controlling the enhancement of brightness. Factor 1.0 always returns a copy of the original image, lower factors mean less color (brightness, contrast, etc), and higher values more. There are no restrictions on this value. Default: 1.0')
    argparser.add_argument('-n', '--name', help = "The filename of output tailed with one of {'.jpg', '.png', '.bmp', '.gif'}. eg. exampl.png")
    argparser.add_argument('-d', '--directory', default = os.getcwd(), help = 'The directory of output.')
    args = argparser.parse_args()
    
    if args.picture and args.picture[-4:]=='.gif':
        print('It may take a while, please wait for minutes...')
    
    try:
        ver, ecl, qr_name = run(
            args.Words,
            args.version,
            args.level,
            args.picture,
            args.colorized,
            args.contrast,
            args.brightness,
            args.name,
            args.directory
            )   
        print('Succeed! \nCheck out your', str(ver) + '-' + str(ecl), 'QR-code:', qr_name)
    except:
        raise