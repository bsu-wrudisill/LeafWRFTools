class init_compare:
    # Spatially aggregates wrfout files using a provided statistic
    # Plotting gets passed off to elsewhere


    def __init__(self, filelist, var):
        self.fx = np.mean
        self.df = pd.DataFrame()        
        self.filelist = filelist
        # loops through the filelist we input


    def time_format(self, ts):
        times_tmp = reduce(lambda x,y: x+y, ts)
        return pd.to_datetime(times_tmp, format='%Y-%m-%d_%H:%M:%S')


    def aggregate_spatial(self, filename, var):
        ds            = Dataset(filename)
        var           = ds.variables[var]
        raw_times     = ds.variables['Times'][:]
        times         = map(self.time_format, raw_times)
        mean_list     = np.asarray(map(lambda X: self.fx(var[X, :, :]), range(len(times))))
        df            = pd.DataFrame(index = times, data=mean_list, columns= [var+'_Mean'])
        self.df       = self.df.append(df)
        ds.close()
    
    def ratio(self,var1,var2):
        var_old = self.var
        self.var = var1
        map(self.aggregate_spatial, self.filelist)
        self.var = var2
        map(self.aggregate_spatial, self.filelist)
        self.var = var_old

    def __call__(self):
        return self.df

