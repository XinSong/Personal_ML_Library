import sys
import random
import math
import numpy
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

def sgd(times, u_start=0,v_start=0,step=0.01):
	u = u_start
	v = v_start
	while times != 0:
		delta_u = round(math.exp(u) + v * math.exp(u*v)-2*v-3,3)
		delta_v = round(2*math.exp(2*v) + u*math.exp(u*v)-2*u-2,3)
		u -= round(step * delta_u,3) 
		v -= round(step * delta_v,3)
		times -= 1
		print u,v,math.exp(u)+math.exp(2*v)+math.exp(u*v)-u*u-2*u*v+2*v*v-3*u-2*v
	print math.exp(u)+math.exp(2*v)+math.exp(u*v)-u*u-2*u*v+2*v*v-3*u-2*v

def logit(x):
	return 1/(1+math.exp(x*-1))

def generateData():
	data = list()
	for i in range(1000):
		x = random.uniform(-1,1)
		y = random.uniform(-1,1)
		if x*x+y*y-0.6 >= 0:
			sign = 1
		else:
			sign = -1
		if random.uniform(0,1) <= 0.1:
			sign *= -1
		data.append((x,y,sign))
	return data

def product(x,y):
	dot_product = 0
	for i in range(len(x)):
		dot_product += x[i]*y[i]
	return dot_product

def sign_logistic(w,x):
	if(logit((product(w,x))) > 0.5):
		return 1
	else:
		return -1

def verify_logistic(w,m_data):
	verification = 0
	for vec in m_data:
		x = vec[0:len(vec)-1]
		y = vec[len(vec)-1]
		if sign_logistic(w,x) == y:
			verification += 1
	return verification*1.0/len(m_data)

def logistic_regression(m_data,times=2000):
	N = len(m_data)
	w = [0]*21
	gradient = [0]*21
	for i in range(2000):
		vec = m_data[i%N]
		x = vec[0:-1]
		y = vec[-1]
		theta = logit(-1*y*product(w,x))
		for index in range(len(x)):
			gradient[index] = theta*(-1*y*x[index])
		for index in range(len(w)):
			w[index] = w[index] - 0.001*gradient[index]
	return w
def main():
	train_data = []
	test_data = []
	for line in open('train.dat','r'):
		vec = line.split()
		vec = [float(item) for item in vec]
		vec[-1] = int(vec[-1])
		vec = [1] + vec
		train_data.append(vec)
	for line in open('test.dat','r'):
		vec = line.split()
		vec = [float(item) for item in vec]
		vec[-1] = int(vec[-1])
		vec = [1] + vec
		test_data.append(vec)
	w=logistic_regression(train_data)
	print 1-verify_logistic(w,test_data)	

if __name__ == '__main__':
	main()
