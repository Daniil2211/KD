def fun(x):
    return x * 2

mass = [1,2,3,4]

result = [y for x in mass if (y := fun(x)) != 4]

print(result)

lines = ['#12', '#23', '44']

if any(((comment := line).startswith('#') for line in lines)):
    print(comment)

res = [any((comment for line in lines if any(comment := line).startswith('#')))]

print(res)