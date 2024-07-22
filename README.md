This notebook uses an API to extract data from DST (Statistikbanken). The py-file draws on the methods from https://github.com/alemartinello/dstapi. 

For each table from DST the setup in the code is as follows:
1. Table summary
2. Display of variable levels to help you find the relevant variable names 
3. Gathering relevant variables to df                                               
4. Changing the df from a long df to a wide one                                    
5. Export to individual excel file

Lastly all the tables are exported as one excel file with multiple sheets.  
