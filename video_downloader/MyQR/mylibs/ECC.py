# -*- coding: utf-8 -*-

from MyQR.mylibs.constant import GP_list, ecc_num_per_block, lindex, po2, log
 
#ecc: Error Correction Codewords
def encode(ver, ecl, data_codewords):
    en = ecc_num_per_block[ver-1][lindex[ecl]]
    ecc = []
    for dc in data_codewords:
        ecc.append(get_ecc(dc, en))
    return ecc

def get_ecc(dc, ecc_num):
    gp = GP_list[ecc_num]
    remainder = dc
    for i in range(len(dc)):
        remainder = divide(remainder, *gp)
    return remainder
    
def divide(MP, *GP):
    if MP[0]:
        GP = list(GP)
        for i in range(len(GP)):
            GP[i] += log[MP[0]]
            if GP[i] > 255:
                GP[i] %= 255
            GP[i] = po2[GP[i]]
        return XOR(GP, *MP)
    else:
        return XOR([0]*len(GP), *MP)
    
    
def XOR(GP, *MP):
    MP = list(MP)
    a = len(MP) - len(GP)
    if a < 0:
        MP += [0] * (-a)
    elif a > 0:
        GP += [0] * a
    
    remainder = []
    for i in range(1, len(MP)):
        remainder.append(MP[i]^GP[i])
    return remainder