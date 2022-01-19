import mysql.connector
import datetime
class DataBase:

    def __init__(self):
        self.mydb = mysql.connector.connect(
                    host="127.0.0.1",
                    user="root",
                    password="Yamahar6$",
                    database="jarvisbb"
                    )
        self.mycursor = self.mydb.cursor(buffered=True)

    def saveToDB(self):
        self.mycursor.execute("COMMIT;")


    def createMeetingsTable(self):
        created = False
        self.mycursor.execute("SHOW TABLES")
        for x in self.mycursor:
            if(x[0] == 'meetings'):
                created = True

        if not created:
            self.mycursor.execute("CREATE TABLE meetings (\
                            id INTEGER NOT NULL AUTO_INCREMENT,\
                            name VARCHAR(255) UNIQUE,\
                            time DATETIME,\
                            PRIMARY KEY (id)\
                            );")
            print('created meetings')

    def createPersonsTable(self):
        created = False
        self.mycursor.execute("SHOW TABLES")
        for x in self.mycursor:
            if(x[0] == 'persons'):
                created = True

        if not created:
            self.mycursor.execute("CREATE TABLE persons (\
                            clientID VARCHAR(255),\
                            PRIMARY KEY (clientID)\
                            );")
            print('created persons')

    def createAttendanceTable(self):
        created = False
        self.mycursor.execute("SHOW TABLES")
        for x in self.mycursor:
            if(x[0] == 'attendance'):
                created = True

        if not created:
            self.mycursor.execute("CREATE TABLE attendance (\
                            pNo VARCHAR(255),\
                            mNo INTEGER,\
                            status VARCHAR(255),\
                            PRIMARY KEY (pNo, mNo),\
                            FOREIGN KEY(mNo) REFERENCES meetings(id)\
                            );")      
            print('created attendance')

    def createTables(self):
        self.createMeetingsTable()
        self.createPersonsTable()
        self.createAttendanceTable()

    def createMeeting(self, name, time):
        sql = "SELECT * FROM meetings WHERE name = %s"
        val = (name,)
        self.mycursor.execute(sql, val)

        if(self.mycursor.rowcount > 0):
            print("meeting already exists: ", name)
            return

        sql = "INSERT INTO meetings (name, time) VALUES (%s, %s);"
        val = (name, time)
        self.mycursor.execute(sql, val)

    def createPerson(self, disc):
        if disc[0:3] != "<@!":
            print("not a valid client ID: ", disc)
            return
        sql = "SELECT * FROM persons WHERE clientID = %s"
        val = (disc,)
        self.mycursor.execute(sql, val)

        if(self.mycursor.rowcount > 0):
            print("person already exists: ", disc)
            return


        sql = "INSERT INTO persons (clientID) VALUES (%s)"
        val = (disc,)
        print(sql, val)
        self.mycursor.execute(sql, val)

    def createAttendance(self, disc, meetingName):
        sql  = "SELECT * FROM meetings WHERE name = %s"
        tpc = (meetingName,)
        self.mycursor.execute(sql, tpc)
        meeting = self.mycursor.fetchone()
        # print(meeting)

        sql = "INSERT INTO attendance (pNo, mNo, status) VALUES (%s, %s, %s)"
        val = (disc, meeting[0], "maybe")
        print(sql, val)
        self.mycursor.execute(sql, val)

    def changeStatus(self, disc, meetingName, newStatus):
        sql  = "SELECT * FROM meetings WHERE name = %s"
        tpc = (meetingName,)
        self.mycursor.execute(sql, tpc)
        meeting = self.mycursor.fetchone()
        print(meeting)

        sql = "UPDATE attendance SET status = %s WHERE pNo = %s AND mNo = %s"
        val = (newStatus, disc, meeting[0])
        print(sql, val)
        self.mycursor.execute(sql, val)

        self.mydb.commit()

        print(self.mycursor.rowcount, " record(s) changed")
        
    def isNotConfirmed(self, disc, meetingName):
        sql  = "SELECT * FROM meetings WHERE name = %s"
        tpc = (meetingName,)
        self.mycursor.execute(sql, tpc)
        meeting = self.mycursor.fetchone()
        print(meeting)

        sql = "SELECT * FROM attendance WHERE pNo = %s AND mNo = %s"
        val = (disc, meeting[0])
        print(sql, val)
        self.mycursor.execute(sql, val)

        if(self.mycursor.rowcount > 0):
            confirm = self.mycursor.fetchone()
            if(confirm[-1] == "maybe"):
                return True

        return False



    def showInfo(self):
        self.mycursor.execute("SELECT * FROM meetings")
        for x in self.mycursor:
            print(x)

        self.mycursor.execute("SELECT * FROM persons")
        for x in self.mycursor:
            print(x)

    def displayAllMeetings(self):
        self.mycursor.execute("SELECT * FROM meetings ORDER BY time")
        returnStr = ""
        for x in self.mycursor:
            x = list(x)
            returnStr = returnStr + x[1] + " " + x[2].strftime("%m/%d/%Y, %H:%M") + "\n"
        
        return returnStr.rstrip()

    def personalMeetings(self, client_id):
        sql = "SELECT name, time FROM meetings INNER JOIN attendance ON mNo = id WHERE status = 'yes' AND pNo = %s ORDER BY time"
        val = (client_id, )
        self.mycursor.execute(sql, val)
        returnStr = ""
        for x in self.mycursor:
            x = list(x)
            returnStr += x[0] + " " + x[1].strftime("%m/%d/%Y, %H:%M") + "\n"
        return returnStr.rstrip()



if __name__ == "__main__":
    db = DataBase()
