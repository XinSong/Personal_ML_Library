import sys
import random
def sign(x):
	if x >= 0:
		return 1
	else:
		return -1

def noise(f_x):
	if random.random() <= 0.2:
		return(f_x * -1)
	else:
		return f_x

def generate_data(seed):
	random.seed(seed)
	m_data = list()
	for i in range(20):
		x = random.uniform(-1,1)
		f_x = sign(x)
		m_data.append((x,noise(f_x)))
	m_data.sort()
	return m_data

def test(m_data,f):
	correct = 0.0
	for item in m_data:
		if f(item[0]) == item[1]:
			correct += 1
	return correct/len(m_data)

def decision_stump(m_data):
	threshold = -1
	s = 1
	optimal_correct = 0
	optimal_threshold = -1
	optimal_s = 1
	f = lambda x:s*sign(x-threshold)
	correct = test(m_data,f)
	if correct > optimal_correct:
		optimal_correct = correct
		optimal_s = s
	s=-1
	correct = test(m_data,f)
	if correct > optimal_correct:
		optimal_correct = correct
		optimal_s = s

	for index in range(len(m_data)-1):
		s=1
		threshold = (m_data[index][0] + m_data[index+1][1])/2
		correct = test(m_data,f)
		if correct > optimal_correct:
			optimal_correct = correct
			optimal_s = s
			optimal_threshold = threshold
		s=-1
		correct = test(m_data,f)
		if correct > optimal_correct:
			optimal_correct = correct
			optimal_s = s
			optimal_threshold = threshold
	return (optimal_s,optimal_threshold,optimal_correct)

def multidimension_decision_stump(m_data,fields=9):
	optimal_correct = 0
	for i in range(fields):
		m_data_segment = []
		for item in m_data:
			m_data_segment.append((item[i],item[fields]))
		s,threshold,correct = decision_stump(m_data_segment)
		print i,correct
		if correct > optimal_correct:
			optimal_correct = correct
			optimal_s = s
			optimal_threshold = threshold
			optimal_index = i
	return (optimal_index,optimal_s,optimal_threshold,optimal_correct)

def readData(file):
	m_data = []
	for line in open(file,'r'):
		line = line.strip()
		m_data_item = line.split()
		m_data_item = [float(m_data_item[i]) if i != len(m_data_item)-1 else int(m_data_item[i]) for i in range(len(m_data_item))] 
		m_data.append(tuple(m_data_item))
	return m_data
	
def main(train_file,test_file):
	m_data = readData(train_file)
	m_test_data = readData(test_file)
	index,s,threshold,correct = multidimension_decision_stump(m_data)
	f = lambda x: s * sign(x-threshold)
	m_test_data_segment = []
	for item in m_test_data:
		m_test_data_segment.append((item[index],item[9]))
	print test(m_test_data_segment,f)

if __name__ == '__main__':
	main(sys.argv[1],sys.argv[2])
