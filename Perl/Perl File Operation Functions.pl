

# Read the contents of a directory
#-----------------------------------------------------------
#!/usr/bin/perl
use strict;
use warnings;

use Path::Tiny;

my $dir = path('foo','bar'); # foo/bar

# Iterate over the content of foo/bar
my $iter = $dir->iterator;
while (my $file = $iter->()) {
    
    # See if it is a directory and skip
    next if $file->is_dir();
    
    # Print out the file name and path
    print "$file\n";
}


#Read an excel Spreadsheet
#-----------------------------------------------------------
use Spreadsheet::Read;

my $workbook = ReadData ("test.xls");
print $workbook->[1]{A3} . "\n";

#Read/write to a file
#-----------------------------------------------------------
#Writing
#----------------------
use Path::Tiny;
#Path::Tiny makes working with directories and files clean and easy to do. Use path() to create a 
#Path::Tiny object for any file path you want to operate on, but remember if you are calling other
#Perl modules you may need to convert the object to a string using 'stringify':
#$file->stringify();
#$dir->stringify();
use autodie; # die if problem reading or writing a file

my $dir = path("/tmp"); # /tmp

my $file = $dir->child("file.txt"); # /tmp/file.txt

# Get a file_handle (IO::File object) you can write to
# with a UTF-8 encoding layer
my $file_handle = $file->openw_utf8();

my @list = ('a', 'list', 'of', 'lines');

foreach my $line ( @list ) {
    # Add the line to the file
    $file_handle->print($line . "\n");
}

#Appending
#----------------------
# As above but use opena_utf8() instead of openw_utf8()
my $file_handle = $file->opena_utf8();

#Reading
#----------------------
my $dir = path("/tmp"); # /tmp
my $file = $dir->child("file.txt");

# Read in the entire contents of a file
my $content = $file->slurp_utf8();

# openr_utf8() returns an IO::File object to read from
# with a UTF-8 decoding layer
my $file_handle = $file->openr_utf8();

# Read in line at a time
while( my $line = $file_handle->getline() ) {
        print $line;
}



