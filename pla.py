import sys
import random
def sign(vec_x, vec_y):
	vec_product = 0
	for index in range(0,len(vec_x)):
		vec_product += vec_x[index] * vec_y[index]
	if vec_product > 0 :
		return 1
	else:
		return -1
def pla(train_data):
	w = [0,0,0,0,0]
	halt = False
	while halt == False:
		halt = True
		for vec in train_data:
			x = vec[0:len(vec)-1]
			y = vec[len(vec)-1]
			if sign(w,x) != y:
				halt = False
				for i in range(0,len(w)):
					w[i] += x[i]*y
	return w

def main(train_file):
	train_data = []
	for line in open(train_file,'r'):
		vec = line.split()
		train_data.append([1] + [float(item) for item in vec])
	print pla(train_data)

if __name__ == '__main__':
	main(sys.argv[1])
