
def get_cookies_from_file(fname='cookies.txt'):
    with open(fname, 'r') as f:
        kvl = []
        for c in f:
            k = c.split()
            for q in k:
                d = {}
                #print(q, end='###\n\n')
                key, value = q.split('=')
                d['name'] = key
                d['value'] = value[:-1]
                kvl.append(d)

        #print(kvl)
    return kvl

if __name__ == '__main__':
    get_cookies_from_file()
