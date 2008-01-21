#Query to Epigrass database to fetch simulation results

library(DBI)
library(RMySQL)
library(lattice)

drv <- dbDriver("MySQL")
con <- dbConnect(drv, username='root',password='mysql', host='localhost',dbname='epigrass')
listTBL <- dbListTables(con)

results<- dbReadTable(con,listTBL[4])
names(results)
par(mfrow=c(2,2))
plot(results$I[results$geocode==230440005],type='l',main='Fortaleza')
plot(results$I[results$geocode==355030800],type='l',main='São Paulo')
plot(results$I[results$geocode==520880605],type='l',main='goianira')
plot(results$I[results$geocode==510760205],type='l',main='Rondonópolis')
x11()
xyplot(I~as.numeric(time),type="l",groups=results$geocode,data=results)
