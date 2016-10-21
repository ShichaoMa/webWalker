import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from cluster_spider import ClusterSpider




def start(spiders, globals, module_name):
    def create(k, v):
        v["__module__"] = module_name
        return type("%sSpider" % k, (ClusterSpider,), v)
    index = 0
    for k, v in spiders.items():
        v.update({"name": k})
        exec("cls_%s = create(k, v)"% index, locals(), globals)
        index += 1

