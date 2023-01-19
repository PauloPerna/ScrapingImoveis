from GetPropertiesData import GetPropertiesData

# Should get data from 250 properties in Ribeirão Preto, SP
df1 = GetPropertiesData("SP","Ribeirão Preto", verbose=True)

# Since the neighborhood is mispelled, should get data from properties in the city
city2 = "São José dos Campos"
state2 = "SP"
neighborhood2 = "Jardim Aquários" 
df2 = GetPropertiesData(state2, city2,neighborhood2)

# Should get data from properties in the neighborhood
city3 = "São José dos Campos"
state3 = "SP"
neighborhood3 = "Jardim Aquárius" 
df3 = GetPropertiesData(state3, city3,neighborhood3)
