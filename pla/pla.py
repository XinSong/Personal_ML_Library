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

def verify(w, train_data):
	verification = 0
	for vec in train_data:
		x = vec[0:len(vec)-1]
		y = vec[len(vec)-1]
		if sign(w,x) == y:
			verification += 1
	return verification/len(train_data)

def pocket(train_data, updates=100):
	w = [0,0,0,0,0]
	w_verification = verify(w,train_data)
	for i in range(0,50):	
		for vec in train_data:
			x = vec[0:len(vec)-1]
			y = vec[len(vec)-1]
			if sign(w,x) != y:
				w_new = w[:]
				for i in range(0,len(w_new)):
					w_new[i] += x[i]*y
				w_new_verification = verify(w_new,train_data)
				if w_new_verification > w_verification:
					w = w_new
					w_verification = w_new_verification
	return w

def main(train_file):
	train_data = []
	for line in open(train_file,'r'):
		vec = line.split()
		train_data.append([1] + [float(item) for item in vec])
	print pla(train_data)

if __name__ == '__main__':
	main(sys.argv[1])
