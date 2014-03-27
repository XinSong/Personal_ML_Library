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
def pla(train_data,seed,updates=None):
	random.seed(seed)
	read_sequence = range(0,len(train_data))
	random.shuffle(read_sequence)
	w = [0,0,0,0,0]
	halt = False
	update_times = 0
	while halt == False:
		halt = True
		for index in read_sequence:
			vec = train_data[index]
			x = vec[0:len(vec)-1]
			y = vec[len(vec)-1]
			if sign(w,x) != y :
				halt = False
				update_times += 1
				for i in range(0,len(w)):
					w[i] += x[i]*y
				if updates != None and update_times == updates:
					halt = True
					break
		random.shuffle(read_sequence)
	return w

def verify(w, train_data):
	verification = 0
	for vec in train_data:
		x = vec[0:len(vec)-1]
		y = vec[len(vec)-1]
		if sign(w,x) == int(y):
			verification += 1
	return float(verification)/len(train_data)
	
def pocket(train_data, seed, updates=100):
	random.seed(seed)
	read_sequence = range(0,len(train_data))
	random.shuffle(read_sequence)
	w = [0,0,0,0,0]
	w_best = w
	w_best_verification = verify(w_best,train_data)
	update_time = 0
	halt = False
	while halt == False:
		halt = True
		for index in read_sequence:
			vec = train_data[index]
			x = vec[0:len(vec)-1]
			y = vec[len(vec)-1]
			if sign(w,x) != int(y):
				halt = False
				update_time += 1
				for i in range(0,len(w)):
					w[i] += x[i]*y
				w_verification = verify(w,train_data)
				if w_verification > w_best_verification:
					w_best = w
				if update_time == updates:
					halt = True
					break
		random.shuffle(read_sequence)
	return w_best

def main(train_file,test_file):
	train_data = []
	for line in open(train_file,'r'):
		vec = line.split()
		train_data.append([1] + [float(item) for item in vec])
	test_data = []
	for line in open(test_file,'r'):
		 vec = line.split()
		 test_data.append([1] + [float(item) for item in vec])
	sum = 0
	for seed in range(0,2000):
		w = pocket(train_data,seed,50)
		print seed,w,verify(w,test_data)
		sum += verify(w,test_data)
	print sum/2000
#	for seed in range(0,2000):
#		sum += pla(train_data,seed)
#	print sum/2000.0

if __name__ == '__main__':
	main(sys.argv[1],sys.argv[2])
