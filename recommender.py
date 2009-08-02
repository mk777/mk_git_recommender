# a mildly intelligent approach
from __future__ import with_statement

from heapq import nlargest
from operator import itemgetter

def Jac_simil(set1,set2):
    """ calculates Jaccard measure of similarity b/w 2 sets"""

    ul = len(set1 & set2)
    if ul == 0:
        return 1.0
    else:
        return float(len(set1 | set2))/ul

class user_data(object):

    def __init__(self,datafilename):
        """ returns the list whose keys are user IDs and the values are the sets of
            repos watched"""
        self.user_data={}
        self.repo_data={}
        for line in open(datafilename,'r'):
            (usr,sep,repo) = line.strip().partition(':')
            self.user_data.setdefault(int(usr),set()).add(int(repo))
            self.repo_data.setdefault(int(repo),set()).add(int(usr))
        self.user_comp_data = dict((k,v) for k,v 
                                   in self.user_data.items() if len(v)>1)
        self.repo_comp_data = dict((k,v) for k,v 
                                   in self.repo_data.items() if len(v)>1)


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

    def repo_simil(self, repoID):
        """ returns a dictionary whose keys are repo IDs and values are 
        similarities"""
        repo_set=self.repo_data[repoID]
        return dict((k,Jac_simil(repo_set,v)) for k,v in 
                    self.repo_comp_data.items())
    
    def user_repo_total_simil(self, userID):
        """return a dicitionnary whose keys are repo IDs and values are 
        the sums of similarity scores over all repos watched by user"""
        result={}

        for repo in self.user_data[userID]:
            for k,v in self.repo_simil(repo).items():
                result[k] = result.get(k,0.0) + v

        return result


    def get_relevance_scores(self,userID):
        """ returns a dictionary whose keys are repo IDs and whose values are
        the coresponding relevance scores """

        #return self.simil_weighted_pref(userID)
        return self.user_repo_total_simil(userID)

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
    #test_list=range(1,5)

    batch_size=1
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
