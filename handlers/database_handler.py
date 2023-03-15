"""Provides a HybridDBhandler class for handling database data. 

This class acts as a switch between a local SQLite database and a remote MongoDB
Atlas database depending on the value of 'use_cloud_database' in the 'config.ini' file.

Classes:
- HybridDBhandler: main class for handling file data.

"""
import configparser

import pymongo
import sqlalchemy
from pymongo import MongoClient
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from local_db.saved_files import Base, SavedFile
from logging_formatter import ConfigLogger


class HybridDBhandler:
    """
    A class for managing hybrid database operations.

    Attributes:
    ----------
    use_cloud_database: bool
        A boolean flag indicating whether to use the cloud database or not.

    local_db: LocalDBManager
        An instance of LocalDBManager to manage the local database.

    cloud_db: CloudDBManager
        An instance of CloudDBManager to manage the cloud database.

    Methods:
    ----------
    insert_file(userid:int, channel_id:int, file_name:str, file_size:str, file_type:str):
        Inserts a file into the database.

    get_files():
        Returns all the files from the database.

    delete_by_channel_id(channel_id):
        Deletes a file from the database by channel id.

    find_by_id(file_id: str):
        Finds a file in the database by its id.

    find_by_filename(filename:str):
        Finds a file in the database by its name.

    find_by_channel_id(channel_id:int):
        Finds a file in the database by its channel id.

    find_name_by_channel_id(channel_id:int):
        Finds the name of a file in the database by its channel id.

    find_fullname_by_channel_id(channel_id:int):
        Finds the full name of a file in the database by its channel id.
    """
    def __init__(self):
        """
        Initializes HybridDBhandler class.
        """
        # config
        config = configparser.ConfigParser()
        config.read('config.ini')
        use_cloud_database_str = config['DEFAULT'].get('use_cloud_database', 'false')
        self.use_cloud_database = use_cloud_database_str.lower() == 'true'
        # database Classes
        self.local_db = LocalDBManager()
        self.local_db.configure_database()

        self.cloud_db = CloudDBManager(config)

    def insert_file(self, userid:int, channel_id:int, file_name:str, file_size:str, file_type:str):
        """
        Inserts a file into the database.

        Parameters:
        ----------
        userid : int
            The user id associated with the file.
        channel_id : int
            The channel id associated with the file.
        file_name : str
            The name of the file.
        file_size : str
            The size of the file.
        file_type : str
            The type of the file.
        """
        if self.use_cloud_database:
            self.cloud_db.insert_file(userid, channel_id, file_name, file_size, file_type)
        self.local_db.insert_file(userid, channel_id, file_name, file_size, file_type)

    def get_files(self):
        """
        Returns all the files from the database.
        """
        if self.use_cloud_database:
            files = self.cloud_db.get_files()
            files = [FileData(f['_id'], f['user_id'], f['channel_id'], f['file_id'], f['file_name'], f['file_size'], f['file_type']) for f in files]
            return files
        files = self.local_db.get_files()
        files = [FileData(f.id, f.user_id, f.channel_id, f.file_id, f.file_name, f.file_size, f.file_type) for f in files]
        return files

    def delete_by_channel_id(self, channel_id):
        """
        Deletes a file from the database by channel id.

        Parameters:
        ----------
        channel_id : int
            The channel id associated with the file.
        """
        if self.use_cloud_database:
            return self.cloud_db.delete_by_channel_id(channel_id)
        return self.local_db.delete_by_channel_id(channel_id)

    def find_by_id(self, file_id: str):
        """
        Finds a file in the database by its id.

        Parameters:
        ----------
        file_id : str
            The id of the file to be searched.

        Returns:
        -------
        FileData or None:
            Returns a FileData object representing the file, or None if the file is not found.
        """
        if self.use_cloud_database:
            return self.cloud_db.find_by_id(file_id)
        return self.local_db.find_by_id(file_id)

    def find_by_filename(self, filename:str):
        """
        Finds a file in the database by its name.

        Parameters:
        ----------
        filename : str
            The name of the file to be searched.

        Returns:
        -------
        List[FileData]:
            Returns a list of FileData objects representing the files with the given name,
             or an empty list if no files are found.
        """
        if self.use_cloud_database:
            return self.cloud_db.find_by_filename(filename)
        return self.local_db.find_by_filename(filename)

    def find_by_channel_id(self, channel_id:int):
        """
        Finds a file in the database by its channel id.

        Parameters:
        ----------
        channel_id : int
            The channel id associated with the file to be searched.

        Returns:
        -------
        List[FileData]:
            Returns a list of FileData objects representing the files with the given channel id
            , or an empty list if no files are found.
        """
        if self.use_cloud_database:
            return self.cloud_db.find_by_channel_id(channel_id)
        return self.local_db.find_by_channel_id(channel_id)

    def find_name_by_channel_id(self, channel_id:int):
        """
        Finds the name of a file in the database by its channel id.

        Parameters:
        ----------
        channel_id : int
            The channel id associated with the file to be searched.

        Returns:
        -------
        str or None:
            Returns the name of the file associated with the given channel id
            , or None if no file is found.
        """
        if self.use_cloud_database:
            return self.cloud_db.find_name_by_channel_id(channel_id)
        return self.local_db.find_name_by_channel_id(channel_id)

    def find_fullname_by_channel_id(self, channel_id:int):
        """
        Finds the full name of a file in the database by its channel id.

        Parameters:
        ----------
        channel_id : int
            The channel id associated with the file to be searched.

        Returns:
        -------
        str or None:
            Returns the full name of the file associated with the given channel id
            , or None if no file is found.
        """
        if self.use_cloud_database:
            return self.cloud_db.find_fullname_by_channel_id(channel_id)
        return self.local_db.find_fullname_by_channel_id(channel_id)

class FileData:
    def __init__(self, id, user_id, channel_id, file_id, file_name, file_size, file_type):
        self.id = id
        self.user_id = user_id
        self.channel_id = channel_id
        self.file_id = file_id
        self.file_name = file_name
        self.file_size = file_size
        self.file_type = file_type

class LocalDBManager:
    def __init__(self):
        """
        Initialize the database manager.
        """
        self.session_maker = None
        
        self.logger = ConfigLogger().setup()
    
    def configure_database(self):
        """configure database for normal programm execution"""
        engine = create_engine("sqlite:///local_db/database.db")
        Base.metadata.create_all(engine)
        self.session_maker = sessionmaker(bind=engine)


    def configure_database_test(self):
        """configures database for test execution"""
        engine = sqlalchemy.create_engine('sqlite:///:memory:')

        Base.metadata.create_all(engine)
        self.session_maker = sqlalchemy.orm.sessionmaker()
        self.session_maker.configure(bind=engine)

    def insert_file(self, userid, channel_id, file_name, file_size, file_type):
        session = self.session_maker()
        # pylint: disable=not-callable
        max_file_id = session.query(func.max(SavedFile.file_id)).scalar() or 0
        file_id = max_file_id + 1
        file = SavedFile(
            file_id=file_id,
            user_id=userid,
            channel_id=channel_id,
            file_name=file_name,
            file_size=file_size,
            file_type=file_type
        )
        session.add(file)
        session.commit()
        session.close()
        self.logger.info("Saved data to local database")

    def get_files(self):
        session = self.session_maker()
        files = session.query(SavedFile).all()
        session.close()
        self.logger.info("Got file data from local database")
        return files

    def delete_by_channel_id(self, channel_id):
        session = self.session_maker()
        file = session.query(SavedFile).filter_by(channel_id=channel_id).first()
        if file is not None:
            session.delete(file)
            self.logger.info("Deleted file with channel_id=%s", channel_id)
            session.commit()
            session.close()
            return True
        else:
            self.logger.info("No file with channel_id=%s found", channel_id)
            session.close()
            return False

    def find_by(self, **kwargs):
        session = self.session_maker()
        file = session.query(SavedFile).filter_by(**kwargs).first()
        session.close()
        return file.channel_id if file else None

    def find_by_id(self, file_id):
        return self.find_by(file_id=file_id)

    def find_by_filename(self, filename):
        return self.find_by(file_name=filename)

    def find_by_channel_id(self, channel_id):
        return self.find_by(channel_id=channel_id)

    def find_name_by_channel_id(self, channel_id):
        session = self.session_maker()
        file = session.query(SavedFile).filter_by(channel_id=channel_id).first()
        session.close()
        return file.file_name if file else "No file found"
    
    def find_fullname_by_channel_id(self, channel_id):
        session = self.session_maker()
        file = session.query(SavedFile).filter_by(channel_id=channel_id).first()
        session.close()
        return f"{file.file_name}.{file.file_type}" if file else "No file found"


class CloudDBManager():
    def __init__(self, config):
        self.config = config

        cluster = MongoClient(config['DEFAULT']['connection_string'])
        self.db = cluster[config['DEFAULT']['cluster_name']]
        self.collection = self.db["file_list"]
        self.counters = self.db["counters"]
        
        self.logger = ConfigLogger().setup()

    def insert_file(self, user_id, channel_id, file_name, file_size, file_type):
        """
        Inserts a new file document into the collection with an auto-incrementing file_id.
        """
        sequence_document = self.counters.find_one_and_update(
            {"_id": "file_id"},
            {"$inc": {"sequence_value": 1}},
            upsert=True,
            return_document=pymongo.ReturnDocument.AFTER,
        )
        file_id = sequence_document["sequence_value"]
        self.collection.insert_one({
            "user_id": user_id,
            "channel_id": channel_id,
            "file_id": file_id,
            "file_name": file_name,
            "file_size": file_size,
            "file_type": file_type
        })
        self.logger.info("Saved data to cloud database")

    def get_files(self):
        results = self.collection.find()
        self.logger.info("Got file data from cloud database")
        return results

    def delete_by_channel_id(self, channel_id):
        result = self.collection.delete_one({"channel_id": channel_id})
        if result.deleted_count == 1:
            self.logger.info("Deleted file with channel_id=%s", channel_id)
            return True
        else:
            self.logger.info("No file with channel_id=%s found", channel_id)
            return False

    def find_by(self, **kwargs):
        result = self.collection.find_one(kwargs)
        return result["channel_id"] if result else None

    def find_by_id(self, file_id):
        return self.find_by(file_id=int(file_id))

    def find_by_filename(self, filename):
        return self.find_by(file_name=filename)

    def find_by_channel_id(self, channel_id):
        return self.find_by(channel_id=int(channel_id))

    def find_name_by_channel_id(self, channel_id):
        result = self.collection.find_one({"channel_id": channel_id}, {"file_name": 1})
        return result.get("file_name", "No file found")

    def find_fullname_by_channel_id(self, channel_id):
        result = self.collection.find_one({"channel_id": channel_id}, {"file_name": 1, "file_type": 1})
        file_name = result.get("file_name", "")
        file_type = result.get("file_type", "")
        full_file_name = file_name + '.' + file_type
        return full_file_name or "No file found"
