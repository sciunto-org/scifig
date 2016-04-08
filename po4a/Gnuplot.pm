# Locale::Po4a::Gnuplot -- Convert plt files to PO file, for translation.
#
# This program is free software; you may redistribute it and/or modify it
# under the terms of GPL (see COPYING).
#

############################################################################
# Modules and declarations
############################################################################

use Locale::Po4a::TransTractor qw(process new);
use Locale::Po4a::Common;

package Locale::Po4a::Gnuplot;

use 5.006;
use strict;
use warnings;

require Exporter;

use vars qw(@ISA @EXPORT $AUTOLOAD);
@ISA = qw(Locale::Po4a::TransTractor);
@EXPORT = qw();

my $debug=0;

sub initialize {}


sub parse {
	my $self=shift;
	my ($line,$ref);
	my $par;

	LINE:
	($line,$ref)=$self->shiftline();

	while (defined($line)) {
		chomp($line);
		print STDERR  "begin\n" if $debug;

        #Ignore the line if it is a comment
		if ($line =~ /^#/) {
            print STDERR  "Comment.\n" if $debug;
        }
        else{
            if ($line =~ /\"/) {
                print STDERR  "Start of line containing \".\n" if $debug;
                # Text before the first quote
                $line =~ m/(^[^"\r\n]*")/;
                my $pre_text = $1;
                print STDERR  "  PreText=".$pre_text."\n" if $debug;
                # The text for translation
                $line =~ m/("[^\r\n]*")/;
                my $quoted_text = $1;
                print STDERR  "  QuotedText=".$quoted_text."\n" if $debug;
                # Text after last quote
                $line =~ m/("[^"\n]*$)/;
                my $post_text = $1;
                print STDERR  "  PostText=".$post_text."\n" if $debug;
                # Remove starting and ending quotes from the translation text, if any
                $quoted_text =~ s/^"//g;
                $quoted_text =~ s/"$//g;
                # Translate the string it
                $par = $self->translate($quoted_text, $ref);
                # Escape the \n characters
                $par =~ s/\n/\\n/g;
                # Now push the result
                $self->pushline($pre_text.$par.$post_text."\n");
                print STDERR  "End of line containing \".\n" if $debug;
            }
            else
            {
                print STDERR "Other stuff\n" if $debug;
                $self->pushline("$line\n");
            }

        }
		# Reinit the loop
		($line,$ref)=$self->shiftline();
	}
}

##############################################################################
# Module return value and documentation
##############################################################################

1;
__END__

=encoding UTF-8

=head1 NAME

Locale::Po4a::Gnuplot - convert plt files from/to PO files

=head1 DESCRIPTION

Locale::Po4a::Gnuplot is a module to help the translation of plt (gnuplot) files into other
[human] languages.

The module searches for lines of the following format and extracts the quoted
text:

plot x**2 title "text than can be translated"


=head1 SEE ALSO

L<po4a(7)|po4a.7>, L<Locale::Po4a::TransTractor(3pm)>.

=head1 AUTHORS

Francois Boulogne <devel at sciunto dot org>

=head1 COPYRIGHT AND LICENSE

Copyright 2006 by BitDefender
Copyright 2012 by Francois Boulogne <devel at sciunto dot org>

This program is free software; you may redistribute it and/or modify it
under the terms of GPL (see the COPYING file).

=cut
