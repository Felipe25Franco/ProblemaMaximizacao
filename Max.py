# -*- coding: utf-8 -*-
"""
Created on Wed Dec 11 09:27:48 2024

@author: Gabriel, Felipe E Samuel
"""
#--------------------------------------------------
# Notas de construçao
#--------------------------------------------------
#f1 e a1, caso existam,  estao associados com a restricao 1 e assim por diante
#o quadro simplex é sempre montado, no ponto de vista das colunas, primeiro vairiaveis, depois todas as variaveis f/a de cada restricao e por fim b
#geralmente "i" esta associado com linhas e j colunas
#--------------------------------------------------
# Imports
#--------------------------------------------------
import pandas as pd
import numpy as np


#--------------------------------------------------
# Setar dados. Pathing do Problema e Metodo
#--------------------------------------------------
#x é o dataframe correspondente ao problema, apenas pra carregar as info e dados
x = pd.read_excel('C:/Users/felip/Desktop/Programação linear/Trabalho/Pasta1.xlsx',index_col=0)  

#!!!!!!!!!!Setar metodo
bigM = True #true big m, flase 2 fases

x = x.fillna(0)#preencher como zero o blank
print("\nProblema:")
print(x)


#--------------------------------------------------
# Funçao iteraçao do simplex (uso posterior)
#--------------------------------------------------
def simplexCalc(simplex):
  #quadro 1
  print("\nQuadro Simplex Inicial:\n")
  simplexDf = pd.DataFrame(data=simplex,index=base,columns=columns)
  print(simplexDf)  
  #Iterações
  lin = np.shape(simplex)[0]#n linha quadro simplex
  col = np.shape(simplex)[1]#n col quadro simplex
  it=0
  znova=simplex[lin-1][0:col-1]
  menor=min(znova)

  while (menor<0):
    cpivo=np.argmin(znova)
    pp=np.array([])
    for i in range(nRes):
        #garante que o pp não será negativo ou gere uma divisão por zero
        if (simplex[i][col-1]<0 or simplex[i][cpivo]<=0):
            pp = np.append(pp,999999)
        else:
            pp = np.append(pp,simplex[i][col-1]/simplex[i][cpivo])
    lpivo=np.argmin(pp)
    numPivo=simplex[lpivo][cpivo]
    
    
    c=np.array([])
    #esc linha pivo
    for j in range (col):
        simplex[lpivo][j]=simplex[lpivo][j]/numPivo
    for i in range (lin):
        c = np.append(c,simplex[i][cpivo])
        
    #esc do resto
    for i in range (lin):
        if i != lpivo:
            for j in range (col):
                simplex[i][j]=simplex[i][j]-c[i]*simplex[lpivo][j]
    base[lpivo]=columns[cpivo]
    
    
     
    it=it+1
    znova=simplex[lin-1][0:col-1]
    menor=min(znova)

  #print quadro simplex final
  print("\nQuadro Simplex Final:\n")
  simplexDf = pd.DataFrame(data=simplex,index=base,columns=columns)
  print(simplexDf)  
  
  return simplex


#--------------------------------------------------
# Montagem quadro Simplex genérico
#--------------------------------------------------

#x = pd.DataFrame()
#contagem de ocorrencias de cada sinal. caso nao tenha add 0
fiSinal = x["sinal"].value_counts()
if (not x["sinal"].isin([">="]).any()):
  fiSinal[">="] = 0
if (not x["sinal"].isin(["<="]).any()):
  fiSinal["<="] = 0
if (not x["sinal"].isin(["="]).any()):
  fiSinal["="] = 0
# numero de variaves normais e numero de restricoes
nVar = x.shape[1] - 2
nRes = x.shape[0] - 1
#numero de colunas do simplex = variaveis + b + numeros de <= + numeros de = + 2 x numeros de >=
nCol = nVar + 1 + fiSinal["<="] + fiSinal["="] + fiSinal[">="]*2 #numero de variaveis+b <= são folgas = é artificial e >= são as folgas e artificial
#numero de linhas do simplex = numero de restricoes + z
nRow = x.shape[0]
#montar o quadro simplex, primeiro peg a parte das variaveis xi
simplex = x.iloc[:, 1:(x.shape[1]-1)].to_numpy()
#ajustar o sinal do z para caso de max
if (x["sinal"].iloc[nRes]=="max"):
   simplex[nRes] = -simplex[nRes]
#criar matriz de zeros do restante e concatenar
simplex = np.concatenate((simplex,np.zeros((x.shape[0],fiSinal["<="] + fiSinal["="] + fiSinal[">="]*2))),axis=1)
#preencher os 1 e -1 de acordo com o tipo da restricao
j = 0
for i in range (nRes):
  if (x.iloc[i,0]=="<="):
    simplex[i, j+nVar] = 1
    j+=1
  elif (x.iloc[i,0]=="="):
    simplex[i, j+nVar] = 1
    if bigM:
      simplex[nRes, j+nVar] = 100000000
    j+=1
  elif (x.iloc[i,0]==">="):
    simplex[i, j+nVar] = -1
    simplex[i, j+1+nVar] = 1
    if bigM:
      simplex[nRes, j+1+nVar] = 100000000
    j+=2
#adicionar a coluna do b
simplex = np.concatenate((simplex,np.transpose([x["b"].to_numpy()])),axis=1)

#columns e base labels montagem inicial
columns = x.columns[1:nVar+1].values
base = np.array([])
for i in range(nRes):
  if (x.iloc[i,0]=="<="):
      columns = np.append(columns, ["f"+str(i+1)])
      base = np.append(base, ["f"+str(i+1)])
  elif (x.iloc[i,0]=="="):
      columns = np.append(columns, ["a"+str(i+1)])
      base = np.append(base, ["a"+str(i+1)])
  elif (x.iloc[i,0]==">="):
      columns = np.append(columns, ["f"+str(i+1)])
      columns = np.append(columns, ["a"+str(i+1)])
      base = np.append(base, ["a"+str(i+1)])
columns = np.append(columns, ["b"])
base = np.append(base, ["z"])

#--------------------------------------------------
# Resolucao de acordo com o metodo
#--------------------------------------------------

if (not x["sinal"].isin([">=","="]).any()):#simplex normal]
   print("\nResolução pelo Simplex Padrão:\n")
   simplex = simplexCalc(simplex)
else:
  if (bigM):
      #Incluindo o M e Zerando os M na linha do z
      j = 0
      for i in range (nRes):
          if (x.iloc[i,0]=="<="):
              j+=1
          elif (x.iloc[i,0]=="="):
              #simplex[nRes, j+nVar] = 100000000
              simplex[nRes] = simplex[nRes] - simplex[nRes, nVar+j]*simplex[i] 
              j+=1
          elif (x.iloc[i,0]==">="):
              #simplex[nRes, j+1+nVar] = 100000000
              simplex[nRes] = simplex[nRes] - simplex[nRes, nVar+j+1]*simplex[i] 
              j+=2
      print("\nResolução pelo BigM:\n")
      simplex = simplexCalc(simplex)
  else:#2fases
     #adicionar z'.
     base = np.append(base, ["z\'"])
     ii=0 # contador da restricao
     flag = True #flg de auxilio
     zlinha = np.zeros((1,nCol))
     for j in range (nCol):#analisar cada coluna
          if j < nVar or j==nCol-1:#se for coluna "normal" de x ou b
            for i in range(nRes):
              if (x.iloc[i,0]==">=" or x.iloc[i,0]=="="): #somar para cada linha q tem a
                zlinha[0,j] -= simplex[i,j]
          else: #caso seja variavel f ou a
            if (x.iloc[ii,0]=="<="): #se <= somar e seguir
                ii+=1
                for i in range(nRes):#somar as linhas certas
                  if (x.iloc[i,0]==">=" or x.iloc[i,0]=="="): #somar para cada linha q tem a
                    zlinha[0,j] -= simplex[i,j]
            elif (x.iloc[ii,0]=="="): # se = ignorar
                ii+=1
            elif (x.iloc[ii,0]==">="): # se >= somar porem usar a flag pra travar uam contagem de ii para ignorar a proxima coluna
                if (flag):
                  for i in range(nRes):#somar as linhas certas
                    if (x.iloc[i,0]==">=" or x.iloc[i,0]=="="): #somar para cada linha q tem a
                      zlinha[0,j] -= simplex[i,j]
                    flag = False
                else:
                  flag = True
                  ii+=1
     
     simplex = np.append(simplex,zlinha, axis=0)
     #simplex 1 fase
     print("\nResolução pelo 2 fases - Etapa 1:\n")
     simplex = simplexCalc(simplex)
     #simplex 2 fase
     #cortar o zlinha e as colunas dos as
     simplex = simplex[:np.shape(simplex)[0]-1,:]
     simplex2 = simplex[:,0:nVar]
     base = base[:np.shape(base)[0]-1]
     #cortar as colunas dos as
     columns0 = columns
     columns = columns0[0:nVar]
     j=nVar # contador das colunas de a e f
     for i in range (nRes):
        if (x.iloc[i,0]=="<="):
           simplex2 = np.append(simplex2,np.transpose([simplex[:,j]]), axis=1)
           columns = np.append(columns,columns0[j])
           j+=1
        elif (x.iloc[i,0]=="="):
           j+=1
        elif (x.iloc[i,0]==">="):
           simplex2 = np.append(simplex2,np.transpose([simplex[:,j]]), axis=1)
           columns = np.append(columns,columns0[j])
           j+=2
     #add b
     simplex2 = np.append(simplex2,np.transpose([simplex[:,nCol-1]]), axis=1)
     columns = np.append(columns,columns0[nCol-1])
     #simplex final
     print("\nResolução pelo 2 fases - Etapa 2:\n")
     simplex = simplexCalc(simplex2)
     
#--------------------------------------------------
# Soluçao final
#--------------------------------------------------

print("\nSolução:\n")
lin = np.shape(simplex)[0]#n linha quadro simplex
col = np.shape(simplex)[1]#n col quadro simplex
#condicao caso for minimizacao inverte o sinal de z
if (x["sinal"].iloc[nRes]=="max"):
  solucao = pd.Series([simplex[lin-1,col-1]],index = [base[lin-1]])
else:
  solucao = pd.Series([-simplex[lin-1,col-1]],index = [base[lin-1]])

#montar a serie soluçao verificando qume esta na base pegar o valor corresponde. quem nao ta atribui zero
for j in range(col-1): 
    if (columns[j] in base):
      solucao = pd.concat([solucao,pd.Series({columns[j]: simplex[np.where(columns[j]==base),col-1][0,0]})])
for j in range(col-1):
    if (not columns[j] in base):
      solucao = pd.concat([solucao,pd.Series({columns[j]: 0})])
solucao = solucao.sort_values(ascending=False)
print(solucao)

#solu so x
print("\nSolução apenas com variáveis x:\n")
solucao2 = pd.Series({'tsts':1})
for j in range(nVar):
  if (columns[j] in base):
      solucao2 = pd.concat([solucao2,pd.Series({columns[j]: simplex[np.where(columns[j]==base),col-1][0,0]})])
solucao2= solucao2[1:]
solucao2 = solucao2.sort_values(ascending=False)
solucao2 = pd.DataFrame(solucao2,columns=["Quantidade"]) 
solucao2["%"] = solucao2["Quantidade"]/solucao2["Quantidade"].sum()*100
print(solucao2)

#lucro
lucro = pd.Series({'tsts':1})
for i in range(lin-1):
  if(base[i] in x.columns):
    if (simplex[i,col-1]*x[base[i]].iloc[lin-1]!=0):
      # print(x[base[i]].iloc[i])
      # print(simplex[i,col-1])
      lucro = pd.concat([lucro,pd.Series({base[i]: simplex[i,col-1]*x[base[i]].iloc[lin-1]})])

print("\nLucro por variável:\n")
lucro= lucro[1:]
lucro = lucro.sort_values(ascending=False)  
lucro = pd.DataFrame(lucro,columns=["Lucro"]) 
lucro["%"] = lucro["Lucro"]/lucro["Lucro"].sum()*100
print(lucro)






























# #mulitplas solu?
# for j in range(col-1):
#     if((not columns[j] in base) and simplex[lin-1,j]==0 and True):
#         print("\nProblema possui múltiplas soluções\n")
#         break

#-----------
#plot
#--------------

# import matplotlib.pyplot as plt
# # ax = solucao[:solucao.shape[0]-2].plot.pie(autopct='%1.1f%%', startangle=90)
# # ax = plt.pie(solucao1[1:])
# # plt.show()
# fig, ax = plt.subplots(1,2)
# solucao1 = solucao1.sort_values(ascending=False)
# #solucao1Lucro = solucao1*
# ax[1].barh(solucao1[1:].index, solucao1[1:])
# ax[1].tick_params(axis='x', labelrotation=90)
# ax[1].set_title("Quantidade")
# # ax[1].bar(lucro.index, lucro)
# # ax[1].set_title("Lucro por variável")
# # ax[1].tick_params(axis='x', labelrotation=90)
# plt.show()
