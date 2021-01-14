from application.models import *
# C:\Users\Ali\Desktop\Lockdown fun\Practice django\KitchenSite
def run():
    f = open('../../../../Hobs.csv', 'r')
    x = f.readlines()
    print(x[:5])

run()