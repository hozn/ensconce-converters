
import gnupg
import yaml
import keepassdb

from ensconce_converters import exc

class KeepassConverter(object):
    """
    Converts the GPG-encrypted YAML produced by Ensconce export to a KDB file.
    """
    
    def __init__(self, inputfile, outputfile, passphrase):
        self.inputfile = inputfile
        self.outputfile = outputfile
        self.passphrase = passphrase
    
    def convert(self):
        """
        Do the conversion.
        """
        gpg = gnupg.GPG()
        
        with open(self.inputfile) as in_fp:
            cleartext = gpg.decrypt_file(in_fp, passphrase=self.passphrase)
        
        data = yaml.load(str(cleartext))
        
        if data is None:
            raise exc.DecryptError("Unable to decrypt GPG file with specified passphrase.")
                
        # First enumerate all the groups present in the file (a resource may belong to multiple groups)
        groups = set()
        for rsc in data['resources']:
            for grpname in rsc['groups']:
                groups.add(grpname)
        
        # Now we can start building up the keepass database, using the same passphrase.
        kdb = keepassdb.Database(password=self.passphrase, new=True)
        
        for groupname in sorted(list(groups)): 
            kdb_group = kdb.create_group(title=groupname)
            
            # Get all the resources that have this group name
            for rsc in [r for r in data['resources'] if groupname in r['groups']]:
                # Add a generic "password" for the resource so we can capture the notes field somewhere.
                kdb_group.create_entry(title=u"(resource) {0}".format(rsc['name']), url=rsc['addr'], notes=u"{0}\n\n{1}".format(rsc['description'], rsc['notes']))
                
                for passwd in rsc['passwords']:
                    kdb_group.create_entry(title=u'[{username}] {resource}'.format(resource=rsc['name'],
                                                                                   username=passwd['username']),
                                           username=passwd['username'],
                                           notes=passwd['description'],
                                           password=passwd['password'])
        
        kdb.save(self.outputfile, password=self.passphrase)