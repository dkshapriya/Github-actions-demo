/**
 * @description       : 
 * @author            : Diksha
 * @group             : 
 * @last modified on  : 09-19-2026
 * @last modified by  : Diksha
**/
@IsTest
private class SalesControllerTest {

    @IsTest
    static void testGetMessage() {
        Test.startTest();

        String result = SalesController.getMessage('Sales');

        Test.stopTest();

        System.assertEquals(
            'Sales button is working!',
            result
        );
    }
}