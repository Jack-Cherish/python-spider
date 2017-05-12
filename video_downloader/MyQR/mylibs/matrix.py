# -*- coding: utf-8 -*-
     
from MyQR.mylibs.constant import alig_location, format_info_str, version_info_str, lindex
    
def get_qrmatrix(ver, ecl, bits):
    num = (ver - 1) * 4 + 21
    qrmatrix = [[None] * num for i in range(num)]
    #  [([None] * num * num)[i:i+num] for i in range(num * num) if i % num == 0] 

    # Add the Finder Patterns & Add the Separators
    add_finder_and_separator(qrmatrix)
    
    # Add the Alignment Patterns
    add_alignment(ver, qrmatrix)
    
    # Add the Timing Patterns
    add_timing(qrmatrix)
    
    # Add the Dark Module and Reserved Areas
    add_dark_and_reserving(ver, qrmatrix)
    
    maskmatrix = [i[:] for i in qrmatrix]
    
    # Place the Data Bits
    place_bits(bits, qrmatrix)
    
    # Data Masking
    mask_num, qrmatrix = mask(maskmatrix, qrmatrix)
    
    # Format Information
    add_format_and_version_string(ver, ecl, mask_num, qrmatrix)

    return qrmatrix

def add_finder_and_separator(m):             
    for i in range(8):
        for j in range(8):
            if i in (0, 6):
                m[i][j] = m[-i-1][j] = m[i][-j-1] = 0 if j == 7 else 1
            elif i in (1, 5):
                m[i][j] = m[-i-1][j] = m[i][-j-1] = 1 if j in (0, 6) else 0  
            elif i == 7:
                m[i][j] = m[-i-1][j] = m[i][-j-1] = 0
            else:
                m[i][j] = m[-i-1][j] = m[i][-j-1] = 0 if j in (1, 5, 7) else 1
    
def add_alignment(ver, m):
    if ver > 1:
        coordinates = alig_location[ver-2]
        for i in coordinates:
            for j in coordinates:
                if m[i][j] is None:
                    add_an_alignment(i, j, m)
            
def add_an_alignment(row, column, m):
    for i in range(row-2, row+3):
        for j in range(column-2, column+3):
            m[i][j] = 1 if i in (row-2, row+2) or j in (column-2, column+2) else 0
    m[row][column] = 1
    
def add_timing(m):
    for i in range(8, len(m)-8):
        m[i][6] = m[6][i] = 1 if i % 2 ==0 else 0
    
def add_dark_and_reserving(ver, m):
    for j in range(8):
        m[8][j] = m[8][-j-1] = m[j][8] = m[-j-1][8] = 0
    m[8][8] = 0
    m[8][6] = m[6][8] = m[-8][8] = 1
    
    if ver > 6:
        for i in range(6):
            for j in (-9, -10, -11):
                m[i][j] = m[j][i] = 0
                
def place_bits(bits, m):
    bit = (int(i) for i in bits)

    up = True
    for a in range(len(m)-1, 0, -2):
        a = a-1 if a <= 6 else a
        irange = range(len(m)-1, -1, -1) if up else range(len(m))
        for i in irange:
            for j in (a, a-1):
                if m[i][j] is None:
                    m[i][j] = next(bit)
        up = not up
  
def mask(mm, m):
    mps = get_mask_patterns(mm)
    scores = []
    for mp in mps:
        for i in range(len(mp)):
            for j in range(len(mp)):
                mp[i][j] = mp[i][j] ^ m[i][j]
        scores.append(compute_score(mp))
    best = scores.index(min(scores))
    return best, mps[best]
    
def get_mask_patterns(mm):
    def formula(i, row, column):
        if i == 0:
            return (row + column) % 2 == 0
        elif i == 1:
            return row % 2 == 0
        elif i == 2:
            return column % 3 == 0
        elif i == 3:
            return (row + column) % 3 == 0
        elif i == 4:
            return (row // 2 + column // 3) % 2 == 0
        elif i == 5:
            return ((row * column) % 2) + ((row * column) % 3) == 0
        elif i == 6:
            return (((row * column) % 2) + ((row * column) % 3)) % 2 == 0
        elif i == 7:
            return 	(((row + column) % 2) + ((row * column) % 3)) % 2 == 0

    mm[-8][8] = None
    for i in range(len(mm)):
        for j in range(len(mm)):
            mm[i][j] = 0 if mm[i][j] is not None else mm[i][j]
    mps = []
    for i in range(8):
        mp = [ii[:] for ii in mm]
        for row in range(len(mp)):
            for column in range(len(mp)):
                mp[row][column] = 1 if mp[row][column] is None and formula(i, row, column) else 0
        mps.append(mp)
        
    return mps
            
def compute_score(m):
    def evaluation1(m):
        def ev1(ma):
            sc = 0
            for mi in ma:
                j = 0
                while j < len(mi)-4:
                    n = 4
                    while mi[j:j+n+1] in [[1]*(n+1), [0]*(n+1)]:
                        n += 1
                    (sc, j) = (sc+n-2, j+n) if n > 4 else (sc, j+1)
            return sc
        return ev1(m) + ev1(list(map(list, zip(*m))))
        
    def evaluation2(m):
        sc = 0
        for i in range(len(m)-1):
            for j in range(len(m)-1):
                sc += 3 if m[i][j] == m[i+1][j] == m[i][j+1] == m[i+1][j+1] else 0
        return sc
        
    def evaluation3(m):
        def ev3(ma):
            sc = 0
            for mi in ma:
                j = 0
                while j < len(mi)-10:
                    if mi[j:j+11] == [1,0,1,1,1,0,1,0,0,0,0]:
                        sc += 40
                        j += 7
                    elif mi[j:j+11] == [0,0,0,0,1,0,1,1,1,0,1]:
                        sc += 40
                        j += 4
                    else:
                        j += 1
            return sc
        return ev3(m) + ev3(list(map(list, zip(*m))))
        
    def evaluation4(m):
        darknum = 0
        for i in m:
            darknum += sum(i)
        percent = darknum  / (len(m)**2) * 100
        s = int((50 - percent) / 5) * 5
        return 2*s if s >=0 else -2*s

    score = evaluation1(m) + evaluation2(m)+ evaluation3(m) + evaluation4(m)
    return score
    
def add_format_and_version_string(ver, ecl, mask_num, m):
    fs = [int(i) for i in format_info_str[lindex[ecl]][mask_num]]
    for j in range(6):
        m[8][j] = m[-j-1][8] = fs[j]
        m[8][-j-1] = m[j][8] = fs[-j-1]
    m[8][7] = m[-7][8] = fs[6]
    m[8][8] = m[8][-8] = fs[7]
    m[7][8] = m[8][-7] = fs[8]
    
    if ver > 6:
        vs = (int(i) for i in version_info_str[ver-7])
        for j in range(5, -1, -1):
            for i in (-9, -10, -11):
                m[i][j] = m[j][i] = next(vs)