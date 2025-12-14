


dict_leaf = {}
dict_nodes = {}



def func_leaf(heap):
    sum = 0
    for (x,y) in heap:
        dict_leaf[y] = 0
        dict_nodes[x] = 0

    for k in dict_nodes.keys():
        sub_sum = 0
        for i in range(len(heap)):
            if heap[i][0] == k:
                if k > heap[i][1]:
                    sub_sum += 1
                else:
                    sub_sum = sub_sum -1   

        if sub_sum >1:
            sum =sum+1    

    sum = sum +(len(list(dict_leaf))-len(list(dict_nodes))+1)

    return sum                   


input = [(70,35),(35,20),(35,10),(70,60),(60,50),(60,30)]

print(func_leaf(input))