import sys

class Node:
	def __init__(self, start, end, prob, total_cases, next):
		self.start = start
		self.end = end
		self.prob = prob
		self.total_cases = total_cases
		self.next = next

def main(train_file):
'''输入文件格式uid，待校验的概率值（比如正样本概率），真实结果（0或者1）
！！！ATTENTION！！！ 需要输入文件已经按照待校验的概率值排序'''
	head = None
	for line in open(train_file,'r'):
		vec = line.split('\t')
		if not head:
			head = Node(float(vec[0]), float(vec[0]), float(vec[1]), 1, None)
			last_node = head
		else:
			last_node.next = Node(float(vec[0]), float(vec[0]), float(vec[1]), 1, None)
			last_node = last_node.next

	completed = False
	while not completed:
		completed = True
		iter = head
		while iter.next:
			if iter.prob >= iter.next.prob:
				iter.end = iter.next.end
				iter.prob = (iter.prob * iter.total_cases + iter.next.prob * iter.next.total_cases) /(iter.total_cases + iter.next.total_cases)
				iter.total_cases = iter.total_cases + iter.next.total_cases
				iter.next = iter.next.next
				completed = False
				break
			iter = iter.next

	iter = head
	while iter:
		print iter.start, iter.end, iter.prob
		iter = iter.next

if __name__ == '__main__':
	main(sys.argv[1])
		
		
