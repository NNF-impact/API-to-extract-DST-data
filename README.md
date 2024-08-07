This notebook uses an API to extract data from DST (Statistikbanken). The py-file draws on the methods from https://github.com/alemartinello/dstapi. 

For each table from DST the steps underneath are present:
1. Table summary
2. Display of variable levels to help you to find the relevant variable codes 
3. Fetch the unit for the table
4. Gathering relevant variables to df                                               
5. Changing the df from a long df to a wide one (and in some df this step changes the variables from stings to numeric variables)                                    
6. Export to individual excel file 

Lastly all the tables are exported as one excel file with multiple sheets.  
