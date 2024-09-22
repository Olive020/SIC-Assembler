# 處理asstest.asm的程式
label, operation, operand, commit = ['']*100, ['']*100, ['']*100, ['']*100
# 記憶體位址
address = ['0x0']*100
# 行數
lineCount = 0
# 程式長度 or PC
programLength = '0x0'
loc='0x0'
# 指令
operationDict = {'ADD': '18', 'ADDF': '58','AND': '40',
                 'COMP': '28','COMPF': '88',
                 'DIV': '24','DIVF': '64',
                 'J': '3C','JEQ': '30','JGT': '34','JLT': '38','JSUB': '48',
                 'LDA': '00','LDB': '68','LDCH': '50','LDF': '70','LDL': '08','LDS': '6C','LDT': '74','LDX': '04','LPS': 'D0',
                 'MULF': '60', 'MUL': '20',
                 'OR': '44',
                 'RD': 'D8','RSUB': '4C',
                 'SSK': 'EC','STA': '0C','STB': '78','STCH': '54','STF': '80','STI': 'D4','STL': '14','STS': '7C','STSW': 'E8','STT': '84','STX': '10','SUB': '1C','SUBF': '5C',
                 'TD': 'E0','TIX': '2C',
                 'WD': 'DC'}
#假指令
pseudoOperationDict = {'START': '0x0', 'END': '0x0', 'BYTE': '0x0', 'WORD': '0x0', 'RESB': '0x0', 'RESW': '0x0'}
# 處理每一行的資料
def extract_data(line):
    global programLength,loc
    labelValue = line[0:9].strip()
    operationValue = line[9:15].strip()
    operandValue = line[17:35].strip()
    commitValue = line[35:].strip()
    loc=programLength
    # address
    if operationValue == 'START':
        # 設定起始位址
        programLength = '0x'+operandValue
        loc=programLength
    elif (operationValue in operationDict) :
        programLength= hex(int(programLength,16) + int('3',16))
    elif operationValue == 'WORD':
        programLength= hex(int(programLength,16) + int('3',16))
    elif operationValue == 'RESW':
        programLength= hex(int(programLength,16) + int(operandValue)*int('3',16))
    elif operationValue == 'BYTE':
        if operandValue[0] == 'X':
            programLength= hex(int(programLength,16) + int((len(operandValue)-3)/2))
        elif operandValue[0] == 'C':
            programLength= hex(int(programLength,16) + int(len(operandValue)-3))
    elif operationValue == 'RESB':
        programLength= hex(int(programLength,16) + int(operandValue))
    else:
        pass
    return labelValue, operationValue, operandValue, commitValue ,loc
labelDict = {}
# 處理asm檔案
def process_asm_file(file_path):
    global lineCount, programLength
    # 開啟檔案
    with open(file_path, 'r') as asm_file:
        # 處理每一行
        for line in asm_file:
            if line[0] == '.':  # 註解
                continue
            label[lineCount], operation[lineCount], operand[lineCount], commit[lineCount] ,address[lineCount]= extract_data(line)
            # 計算行數
            lineCount += 1
            if operation[lineCount-1]=='START':
                print('從地址: ',int(operand[lineCount-1]),'開始',label[lineCount-1])
                labelDict.update({label[lineCount-1]:address[lineCount-1]})
            elif operation[lineCount-1]=='END':
                programLength=hex(int(programLength,16)-int(address[0],16))#計算程式長度
                print('程式長度: ',programLength[2:])
                break
            elif len(label[lineCount-1])!=0:
                labelDict.update({label[lineCount-1]:address[lineCount-1]})
def write_file(file_path):
    objFile = open(file_path, 'w')
    for i in range(lineCount):
        if i==0:
            objFile.write('H'+label[i].ljust(6)+address[i][2:].rjust(6,'0')+programLength[2:].rjust(6,'0')+'\n')
        elif operation[i] in operationDict:
            if ',X' in operand[i]:
                operand[i], x = operand[i].split(',')
                if operand[i].isdigit():
                    objFile.write('T'+address[i][2:].rjust(6,'0')+'03'+operationDict[operation[i]]+hex(int(operand[i],16)+int('8000',16))[2:]+'\n')
                else:
                    objFile.write('T'+address[i][2:].rjust(6,'0')+'03'+operationDict[operation[i]]+hex(int(labelDict[operand[i]],16)+int('8000',16))[2:]+'\n')
                
            else:
                if operation[i] =='RSUB':
                    objFile.write('T'+address[i][2:].rjust(6,'0')+'03'+operationDict[operation[i]]+'0000'+'\n')
                else:
                    if operand[i].isdigit():
                        objFile.write('T'+address[i][2:].rjust(6,'0')+'03'+operationDict[operation[i]]+hex(int(operand[i],16))[2:].rjust(4,'0')+'\n')
                    else:
                        opadd=labelDict[operand[i]][2:].rjust(4,'0')
                        objFile.write('T'+address[i][2:].rjust(6,'0')+'03'+operationDict[operation[i]]+opadd+'\n')
        elif operation[i]=='WORD':
            objFile.write('T'+address[i][2:].rjust(6,'0')+'03'+hex(int(operand[i]))[2:].rjust(6,'0')+'\n')
        elif operation[i]=='BYTE':
            #16進位
            if operand[i][0]=='X':
                byte_leng=str(round((len(operand[i])-3)/2)).rjust(2,'0')
                objFile.write('T'+address[i][2:].rjust(6,'0')+byte_leng+operand[i][2:-1]+'\n')
            #ASCII
            else:
                str_leng=str(len(operand[i][2:-1])).rjust(2,'0')
                str_ascii=operand[i][2:-1].encode('utf-8').hex()
                objFile.write('T'+address[i][2:].rjust(6,'0')+str_leng+str_ascii+'\n')
        elif operation[i]=='END':
            objFile.write('E'+labelDict[operand[i]][2:].rjust(6,'0')+'\n')
        

def main():
    asm_path = 'example2-1.asm'
    obj_path ,asm= asm_path.split('.')
    process_asm_file(asm_path)#pass1
    print(labelDict)
    write_file(obj_path+'.obj')#pass2


if __name__ == '__main__':
    main()
