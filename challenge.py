import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations

## 10진수를 l비트의 2진수로 변환
def binary(num, l) :
    c = format(num,'b')
    while len(c) < l :
        c = "0"+c
    return c

## 해밍디스턴스 계산 
def compare(a,b) :
    cnt = 0
    ret = [] # 다른 자릿수
    i = len(a)
    while True :
        i = i - 1
        if i == - 1 :
            break
        if a[i] != b[i] :
            cnt = cnt + 1
            ret.append(i)
        ## 다른게 2개면 즉시 종료
        if cnt == 2 :
            return 2, 0
    return cnt, ret

# Pi영역에 숫자(민텀)가 들어가있는지 확인
def contain_num(num, p) :
    n = binary(num,len(p))
    for i in range(len(n)) :
        if n[i] == p[i] or p[i] == '2' or p[i] == '-':
            continue
        else :
            return False
    return True

def find_PI_EPI(minterm):
    answer = []
    num = minterm[0] # 비트수
    #num_minterm = minterm[1] # minterm의 개수
    mint = minterm[2:] # minter#1 ~
    bi = [[] for _ in range(num+1)] # 비트가 n이므로 1은 0~num까지 n+1개의 공간이 필요함 2차원 배열로 만들어줌
    #max = 0 # 1이 가장 많이 나온 
    # 처음 minterm이 있는 첫번째 table
    for i in mint :
        a = binary(i,num)
        b = a.count('1') # 1의 갯수
        bi[b].append([str(a),0]) # 이진수와 0 -> vaild비트 b -> 1의 갯수
    while True :
        new =  [[] for _ in range(len(bi))]
        changed = False # 새로운 테이블이 만들어 지나 확인
        for i in range(len(bi)-1) :
            for j in range(len(bi[i])) :
                for k in range(len(bi[i+1])):
                    cnt, diff = compare(bi[i][j][0], bi[i+1][k][0])
                    #print(bi[i][j],bi[i+1][k],cnt)
                    if cnt == 1 : # 해밍디스턴스 1
                        changed = True # 변화 발생
                        new_num = bi[i][j][0][:diff[0]] + "2" + bi[i][j][0][diff[0]+1:] # '-'로하게되면 정렬할 때 불편함을 겪어 일단은 2로 넣어줌
                        # vaild 수정
                        bi[i][j][1] = 1 
                        bi[i+1][k][1] = 1
                        if [new_num,0] not in new[new_num.count('1')] :
                            new[new_num.count('1')].append([new_num, 0])
                    elif i == len(bi)-1 and bi[i+1][k][1] == 0 :
                        answer.append(bi[i+1][k][0]) 
                if bi[i][j][1] == 0 :
                    answer.append(bi[i][j][0])
        # 새로운 테이블
        bi = new
        # 변화가 없으면 while문 종료
        if changed == False :
            break   
    # 중복제거
    answer = list(set(answer))
    # 정렬
    answer = sorted(answer)
    ans = []
    nepi = []
    PI = []
    EPI = []
    # 정렬을 위해 사용했던 '2'를 '-'로 바꿔줌
    for i in answer :
        ans.append(i.replace('2', '-'))
        PI.append(i.replace('2','-'))
        nepi.append(i)
    ans.append("EPI")
    nepi2 = []

    ## nepi넣어주기
    for x in mint :
        cnt = 0
        tmp = ""
        for y in nepi :
            if contain_num(x,y) :
                cnt += 1
                tmp = y
            if cnt == 2 :
                break
        if cnt == 1 and tmp not in nepi2:
            nepi2.append(tmp)

    nepi2 = sorted(nepi2)
    for i in nepi2 :
        ans.append(i.replace('2', '-'))
        EPI.append(i.replace('2', '-'))
    return PI, EPI # PI, EPI return


def row_dominance(not_EPI_minterm, table) :
    new_table = []
    if len(table) == 1 :
        return not_EPI_minterm, table
    
    # PI와 해당 PI가 가지고 있는 NEPI minterm 값들을 담는 리스트를 만든다.
    for PI in table :
        a = set()
        for mint in not_EPI_minterm :
            if contain_num(mint, PI) :
                a.add(mint)
        new_table.append([PI, a])
    
    # 지배당하는 PI 제거 하기 
    for i in range(len(new_table)-1) :
        for j in range(i+1, len(new_table)) :
            # 길이가 더 작은쪽에 대해서 길이가 더 큰 쪽의 부분집합인지 확인
            if len(new_table[i][1]) > len(new_table[j][1]) :
                if new_table[j][1].issubset(new_table[i][1]) : # issubset() -> 부분 집합인지 확인
                    new_table[j] = [0,set()] 
            else :
                if new_table[i][1].issubset(new_table[j][1]) :
                    new_table[i] = [0,set()]
    
    # 리턴값 
    ret_PI = [] # 지배안되는 PI 즉 리턴값
    for ret in new_table :
        if ret == [0,set()] :
            continue
        else :
            ret_PI.append(ret[0])
    # print("-----row dominance result-----")
    # print("해당 minterm: ", not_EPI_minterm, "지배하는 PI목록:", ret_PI)
    return not_EPI_minterm, ret_PI


def col_dominance(not_EPI_minterm, PI) :
    new_table = []
    if len(not_EPI_minterm) == 1 :
        return not_EPI_minterm, PI

    # 해당 minterm이 가지고 있는 PI 값들을 담는 리스트를 만든다.
    for mint in not_EPI_minterm :
        a = set()
        for P in PI :
            if contain_num(mint, P) :
                a.add(P)
        new_table.append([mint, a])
    
    # 지배 하는 minterm을 제거한다
    delete_min = []
    for i in range(len(new_table)-1) :
        for j in range(i+1, len(new_table)) :
            # 길이가 더 작은쪽에 대해서 길이가 더 큰 쪽의 부분집합인지 확인
            if len(new_table[i][1]) > len(new_table[j][1]) :
                if new_table[j][1].issubset(new_table[i][1]) : 
                    #new_table[i] = [0,set()]
                    delete_min.append(new_table[i])
            else :
                if new_table[i][1].issubset(new_table[j][1]) :
                    #new_table[j] = [0,set()]
                    delete_min.append(new_table[j])

    # 리턴값
    ret_minterm = [] # 지배안되는 PI 즉 리턴값
    for ret in new_table :
        if ret in delete_min :
            continue
        else :
            ret_minterm.append(ret[0])
    # print("-----col dominance result-----")
    # print("해당 minterm: ", ret_minterm, "PI목록:", PI)
    return ret_minterm, PI


def find_EPI(minterm, PI) :
    ## nepi넣어주기
    nepi2 = []
    EPI = []
    for x in minterm :
        cnt = 0
        tmp = ""
        for y in PI :
            if contain_num(x,y) :
                cnt += 1
                tmp = y
            if cnt == 2 :
                break
        if cnt == 1 and tmp not in nepi2:
            nepi2.append(tmp)

    nepi2 = sorted(nepi2)
    for i in nepi2 :
        EPI.append(i.replace('2', '-'))
    
    return EPI

def loop_dominance(minterm) :
    # find all PI and EPI
    PI, EPI = find_PI_EPI(minterm)
    
    # petrick 예시
    # PI = ['000-','00-0','0-01','0-10', '01-1','011-']
    # EPI = []
    # minterm = [0,1,2,5,6,7]

    EPIs = [] # 선택된 PI들 즉 EPI
    #print("start PI: ", PI,"EPI: ", EPI, "minterm: ", minterm[2:])
    minterm = minterm[2:]
    cnt = 1

    while True :
        # simplify the table 
        print()
        print(cnt, "번 반복")
        cnt = cnt + 1
        print("테이블 정보")
        print()
        draw_table(PI, minterm)
        print()
        print()

        NEPI = list(set(PI) - set(EPI)) # EPI를 제거한 PI list -> NEPI
        for sel in EPI :
            EPIs.append(sel)

        EPI_minterm_set = set()
        for x in minterm :
            for y in EPI :
                if contain_num(x,y) :
                    EPI_minterm_set.add(x)
        
        not_EPI_minterm = list(set(minterm) - EPI_minterm_set)
        if len(not_EPI_minterm) == 0 : PI = []

        #print("EPI에 포함된 minterm제거: ", not_EPI_minterm)
        "EPI를 제거할 때는 EPI의 열과 해당되는 minterm 제거"
        print("EPI 제거 후 테이블 정보")
        print()
        draw_table(NEPI, not_EPI_minterm)
        print("EPI:", EPI)
        print()
        if len(NEPI) == 0 :
            print("NEPI가 존재하지 않음")
            print()
            print()
            PI = []
            minterm = []
            break

        # Apply column dominance law
        col_minterm, col_PI = col_dominance(not_EPI_minterm, NEPI)
        print("col_dominance 이후 테이블 정보")
        print()
        draw_table(col_PI, col_minterm)
        print()
        print()

        # Apply row dominance law
        row_minterm, row_PI = row_dominance(col_minterm, col_PI)
        print("row_dominance 이후 테이블 정보")
        print()
        draw_table(row_PI, row_minterm)
        print()
        print()

        # 다시 반복하는지
        if PI == row_PI and minterm == row_minterm : 
            PI, minterm, EPIs = Petrick(PI, minterm, EPIs)
            break
        elif len(not_EPI_minterm) == 0 :
            PI = []
            print()
            print("테이블에 남아있는 PI, minterm이 없습니다.")
            draw_table(PI, row_minterm)
            print()

            return PI, row_minterm, EPIs
        else :
            PI = row_PI
            minterm = row_minterm
            EPI = find_EPI(minterm, PI)
    return PI, minterm, EPIs # 남아있는 PI, minterm 그리고 지금까지 찾은 EPI모음
    

def draw_table(PI, minterm) :
    table = []
    new_PI = []
    sorted_PI = []

    # sort PI :
    for p in PI :
        new_PI.append(p.replace('-','2')) 
    new_PI = sorted(new_PI)
    for q in PI :
        sorted_PI.append(q.replace('2','-'))


    for x in sorted_PI :
        check_minterm = []
        for mint in minterm :
            if contain_num(mint, x) :
                check_minterm.append('V')
            else :
                check_minterm.append(".")
        table.append(check_minterm)
    col = minterm
    ind = PI
    con = table
    if len(col) == 0 :
        ind = []
    if len(PI) == 0 :
        col = []
    df = pd.DataFrame(con, columns=col, index = ind)
    print(df)


# 식 전개
def Petrick(PI, minterm, EPIs) :
    EPIs.append("after Petrick")
    print("Petrick")
    busket = []
    nickname = []
    cnt = 1
    for x in PI :
        nick = "P" + str(cnt)
        cnt += 1
        nickname.append((nick, x))

    for i in minterm :
        a = []
        for nick, P in nickname :
            if contain_num(i,P) :
                a.append(nick)
        busket.append(a)

    for i in range(1, len(busket)) :
        tmp = mul(busket[0], busket[i])
        busket[0] = tmp

    min_len = 999999 # 가장 적은 경우 뽑음
    for F in busket[0] :
        if len(set(F.split('P'))) < min_len :
            P = set(F.split('P'))
            min_len = len(set(F.split('P')))
    P = list(P)
    #print(P[1:], min_len-1)
    #select_PI = []
    for nick, Pi in nickname :
        if nick[1:] in P[1:] :
            EPIs.append(Pi)

    return PI, minterm, EPIs

def mul(a,b) :
    ret = list()
    for x in a :
        for y in b :
            ret.append(x + y)
    return ret
    


"""
    loop_dominance 원리
    입력 : ([변수의 개수, minterm의 개수, minterm #1, minterm #2, ....])
    출력 : 최소화하고 남은 PI와 minterm 출력, 그리고 지금꺼 지운 EPI들 출력
    
    동작 원리 
    1. 과제에서 구현했던 함수를 통해 PI, EPI를 구한다
    2. PI에서 EPI와 그 안에 속한 minterm을 제거해 준다. -> NEPI를 남김 NEPI가 없다면 그대로 종료
    3. column dominance raw를 적용
    4. row dominacne raw를 적용
    5. 적용후 table이 간단해지면 다시 PI, EPI, minterm을 새로 갱신하고 다시 반복문 수행
    그렇지 않으면 반복을 종료한다

"""



### case 정보

"""
    1. Petrick 활용
    petrick으로 가는 예시
    과제 형식의 입력 ([변수의 개수, minterm의 개수, minterm #1, minterm #2, ....])
    minterm = [4,6, 0,1,2,5,6,7]
"""
print("test case 1")
PI, minterm, EPIs =  loop_dominance([4,6, 0,1,2,5,6,7])
print("dominance 후 최종 테이블")
print()
draw_table(PI, minterm)
print()
print("dominance 반복과정을 하며 선택된 EPI들",EPIs)


"""
    2. 예시2
    과제 형식의 입력 ([변수의 개수, minterm의 개수, minterm #1, minterm #2, ....])
    minterm = [4,8,0,4,8,10,11,12,13,15]
"""
print("test case 2")
PI, minterm, EPIs =  loop_dominance([4,8,0,4,8,10,11,12,13,15])
print("dominance 후 최종 테이블")
print()
draw_table(PI, minterm)
print()
print("dominance 반복과정을 하며 선택된 EPI들",EPIs)

"""
    3. 예시3
    과제 형식의 입력 ([변수의 개수, minterm의 개수, minterm #1, minterm #2, ....])
    minterm = [4, 11, 0,2,5,6,7,8,10,12,13,14,15]
"""
print("test case 3")
PI, minterm, EPIs =  loop_dominance( [4, 11, 0,2,5,6,7,8,10,12,13,14,15])
print("dominance 후 최종 테이블")
print()
draw_table(PI, minterm)
print()
print("dominance 반복과정을 하며 선택된 EPI들",EPIs)

"""
    4. 예시4
    과제 형식의 입력 ([변수의 개수, minterm의 개수, minterm #1, minterm #2, ....])
    minterm = [5, 20, 0,2,5,6,7,8,10,12,13,14,15, 22,23,24,25,26,27,28,29,30]

"""
print("test case 4")
PI, minterm, EPIs =  loop_dominance([5, 20, 0,2,5,6,7,8,10,12,13,14,15, 22,23,24,25,26,27,28,29,30])
print("dominance 후 최종 테이블")
print()
draw_table(PI, minterm)
print()
print("dominance 반복과정을 하며 선택된 EPI들",EPIs)

