/**
 * @description       : 
 * @author            : Diksha
 * @group             : 
 * @last modified on  : 09-19-2026
 * @last modified by  : Diksha
**/
public with sharing class SalesController {
    @AuraEnabled(cacheable=true)
    public static String getMessage(String department) {
        return department + ' button is working!';
    }
}