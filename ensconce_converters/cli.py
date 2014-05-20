import os
import sys
import optparse
import getpass
import logging

from ensconce_converters.convert import KeepassConverter

def keepass(argv=None):
    if argv is None:
        argv = sys.argv
        
    parser = optparse.OptionParser(usage="usage: %prog -i INPUTFILE -o OUTPUTFILE",
                                   description='Convert GPG-encrypted Esconce export YAML to Keepass 1.x DB.')
    
    
    parser.add_option('-d', '--debug',
                      default=False,
                      action="store_true",
                      help='Run in debug mode?')
   
    # Allowing the password to be specified on the commandline seems to be encouraging
    # bad security practices. 
    #
    #parser.add_option('-p', '--passphrase',
    #                  metavar='SECRET',
    #                  help="The passphrase to use for both the GPG decrypt and creating KeePass datatabase (leave empty to prompt).")
    
    parser.add_option('-i', '--input',
                      metavar='FILE',
                      help="The GPG-encrypted Ensconce YAML export file to convert.")
    
    parser.add_option('-o', '--output',
                      metavar='FILE',
                      help="The KeePass 1.x database file to create.")
    
    
    (options, args) = parser.parse_args()
  
    logging.basicConfig(level=logging.DEBUG if options.debug else logging.INFO)
    
    #if not options.passphrase:
    #    parser.error("passphrase is required")
    
    if not options.input:
        parser.error("input file must be specified")
        
    if not options.output:
        parser.error("output file must be specified")
        
    passphrase = getpass.getpass("Passphrase: ")
    
    #if not options.passphrase:
    #    passphrase = getpass.getpass("Passphrase (for GPG input and for KDB): ")
    #else:
    #    passphrase = options.passphrase
          
    converter = KeepassConverter(inputfile=os.path.abspath(options.input),
                                 outputfile=os.path.abspath(options.output),
                                 passphrase=passphrase)
    converter.convert()
    
    
    