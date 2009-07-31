# this is the simplest, dirtiest, brutest approach to the task

from heapq import nlargest
from operator import itemgetter

def Jac_simil(set1,set2):
    """ calculates Jaccard measure of similarity b/w 2 sets representing repos
        two users are watching"""

    ul = len(set1 & set2)
    if ul == 0:
        return 1.0
    else:
        return float(len(set1 | set2))/ul

class user_data(object):

    def __init__(self,datafilename):
        """ returns the list whose keys are user IDs and the values are the sets of
            repos watched"""
        result = {}
        for line in open(datafilename,'r'):
            (usr,sep,repo) = line.strip().partition(':')
            result.setdefault(int(usr),set()).add(int(repo))

        self.user_data = result

    def simil_weighted_pref(self,userID):
        """ returns a dictionary whose keys are repo IDs and values are
            similarity-weighted average numbers of wathces for the repo
            corresponding to the key. The values are used as relevance
            scores."""

        user_set = self.user_data[userID]
        result = {}
        total_weight=0.0
        for k,v in self.user_data.iteritems():
            w = Jac_simil(user_set,v)
            for repo in v:
                result[repo] = result.get(repo,0.0)+w
                total_weight += w
        total_weight -= 1.0 # remove the effect of the step where v==user_set

        #we are not interested in scores of the repos already watched by the
        #user
        for repo in user_set:
            del result[repo]
      
        for repo in result.keys():
            result[repo] /= total_weight;
        return result;

    def get_relevance_scores(self,userID):
        """ returns a dictionary whose keys are repo IDs and whose values are
        the coresponding relevance scores """

        return self.simil_weighted_pref(userID)

    def get_user_candidates(self,userID,num_cand):
        """ returns the list of num_cand most relevant candidates to be
            suggested to the user based on the get_relevance_scores(userID)"""
        try:
            user_set = self.user_data[userID]
            rel_scores = self.get_relevance_scores(userID)
            return dict(nlargest(num_cand,rel_scores.iteritems(),key = itemgetter(1)))
        except KeyError:
            return dict()

def get_test_user_list(filename):
    """ Read the test user IDs from a file """

    return [int(line) for line in open(filename,'r')]

def get_candidates(userlist, udata, num_candidates):
    """returns a dictionary whose keys are users and values are lists of
    num_candidates worth of most likely candidates for the corresponding user
    to watch"""

    return dict((uid,udata.get_user_candidates(uid,num_candidates).keys())
                for uid in userlist)
def print_results(cand_dict,filename,mode):
    """ write a results file in the specified format"""

    with open(filename,mode) as f:
        for k,v in sorted(cand_dict.items()):
            f.write(str(k)+":"+",".join(map(str,v))+"\n")
            
def _main():
    data_filename = "data.txt"
    test_filename = "test.txt"
    result_filename = "results.txt"
    #clear the result file
    with open(result_filename,'w') as f:
        pass
    
    usr_data = user_data(data_filename)
    test_list = get_test_user_list(test_filename)

    batch_size=100
    test_len=len(test_list)
    print "test length: "+str(test_len)
    print "batch size: "+str(batch_size)
    
    for i in range(0,test_len/batch_size+1):
        i1=i*batch_size
        i2=min(test_len,i1+batch_size)
        candidates=get_candidates(test_list[i1:i2],usr_data,10)
        print_results(candidates,result_filename,'a')
        print "batch "+str(i+1)+" done"

if __name__ == '__main__':
    _main()
