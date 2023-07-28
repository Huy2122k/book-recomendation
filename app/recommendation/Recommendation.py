

class Recommendation(object):

    def __init__(self, *args):
        super(Recommendation, self).__init__(*args)
    
    def get_model(self):
        raise NotImplementedError()
    
    def save_model(self):
        raise NotImplementedError()
    
    def process_data(self):
        raise NotImplementedError()
    
    def predict(self, *args):
        raise NotImplementedError()




