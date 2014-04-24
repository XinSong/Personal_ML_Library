import sys

class Node:
	def __init__(self, start, end, prob, total_cases, unpaidfundsnapshot, fund, next, unpaidfund, unpaid_cases):
		self.start = start
		self.end = end
		self.prob = prob
		self.total_cases = total_cases
		self.unpaidfundsnapshot = unpaidfundsnapshot
		self.fund = fund
		self.next = next
		self.unpaidfund = unpaidfund
		self.unpaid_cases = unpaid_cases

def main(train_file):
'''输入文件格式uid，待校验的概率值（比如正样本概率），真实结果（0或者1）
！！！ATTENTION！！！ 需要输入文件已经按照待校验的概率值排序'''
	head = None
	for line in open(train_file,'r'):
		vec = line.split('\t')
		if not head:
			head = Node(float(vec[0]), float(vec[0]), float(vec[1]), 1, float(vec[2]), float(vec[3]), None, float(vec[3]) if float(vec[2]) else 0, 1 if float(vec[2]) else 0 ) 
			last_node = head
		else:
			last_node.next = Node(float(vec[0]), float(vec[0]), float(vec[1]), 1, float(vec[2]), float(vec[3]), None, float(vec[3]) if float(vec[2]) else 0, 1 if float(vec[2]) else 0 ) 
			last_node = last_node.next

	completed = False
	while not completed:
		completed = True
		iter = head
		while iter.next:
			if iter.prob >= iter.next.prob or iter.total_cases < 100:
				iter.end = iter.next.end
				iter.prob = (iter.prob * iter.total_cases + iter.next.prob * iter.next.total_cases) /(iter.total_cases + iter.next.total_cases)
				iter.total_cases = iter.total_cases + iter.next.total_cases
				iter.unpaidfundsnapshot = iter.unpaidfundsnapshot + iter.next.unpaidfundsnapshot
				iter.fund = iter.fund + iter.next.fund
				iter.unpaidfund = iter.unpaidfund + iter.next.unpaidfund
				iter.unpaid_cases = iter.unpaid_cases 
				iter.next = iter.next.next
				completed = False
				break
			iter = iter.next

	iter = head
	while iter:
		print iter.start, iter.end, iter.prob, iter.total_cases, iter.unpaidfundsnapshot/iter.fund, round(iter.total_cases * iter.prob)
		iter = iter.next

if __name__ == '__main__':
	main(sys.argv[1])
