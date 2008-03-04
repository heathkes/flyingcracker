#!/usr/bin/perl
use Socket;
use CGI qw(:standard escape);

$IS_TRIAL = 0;

#
# Change to name of BUGZ server
#
$BUGZ_SERVER = "graham.fogbugz.com";

#
# Change only if you aren't running on normal port 80
#
$BUGZ_PORT = "80";

#
# Change to top level URL for bugz server - must contain trailing slash
#
$BUGZ_URL = "/";

#
# If you're hosting FogBugz with PHP on Unix or Macintosh, change to "cvsSubmit.php"
# Otherwise, (including FogBugz On Demand accounts) this should be "cvsSubmit.asp"
#
$CVSSUBMIT = "cvsSubmit.asp";

######### That's all you have to do! ###########
#                                              #
#                                              #
#  You shouldn't need to edit anything below   #
#                  here!                       #
################################################

$TRIAL_ID = "";

$BUGZ_URL_FINAL = "http:\/\/".$BUGZ_SERVER.":".$BUGZ_PORT.$BUGZ_URL;
if ($IS_TRIAL)
{
	$BUGZ_URL_FINAL = "https://graham.fogbugz.com/"; # This line replaced automatically when script is downloaded from trial
}

$sTrialClause = "";
if ($IS_TRIAL && length($TRIAL_ID) > 0)
{
	$sTrialClause = "&id=" . $TRIAL_ID;
}

$wget = 0;

$wget_path = "/usr/bin/wget";
chomp($wget_path);
if ( -e $wget_path )
{ 
 $wget = 1; 
} else {
 $wget_path = "/usr/local/bin/wget";
 if ( -e $wget_path ) { $wget = 1; }
}


$logmsg = "";
while (<STDIN>)
{
	$logmsg .= $_;
}

#
# Get BUG number if its there
#
$bugIDString = "";
@rgLine = split("\n", $logmsg);

foreach (@rgLine)
{
	if ($_ =~ /\s*Bug[zs]*\s*IDs*\s*[#:; ]+((\d+[ ,:;#]*)+)/i)
	{
		$bugIDString .= " " . $1;
	}
}

#print "Log Message: $logmsg\n";
#print "Bug ID String: $bugIDString\n";

#
# Read the SVNLOOK CHANGED info from a file specified on the command line
#
open FILE, $ARGV[1] or die "Can't open $ARGV[1] :: $! ::";
while ( <FILE> ) {
	$sChangeInfo .= $_;
} close FILE or die "Can't close $ARGV[1] :: $! ::";
#print "Change Info: $sChangeInfo\n";

#
# For each file open a socket to the right port on the bugz server and submit
# data through a GET request
#
# Pattern splits the changes info into change type/filename sections
#

#
# Now, do the submission. We loop through the bug IDs, and submit
# all checked in files against each in turn.
#

@bugIDlist = split("[ ,:;#]+", $bugIDString);

foreach (@bugIDlist)
{
	if (/\d+/)
	{
		$ixBug = int($_);

		print "Adding bug info for Bug ID #$ixBug...\n";

		foreach $sChangeLine (split("\n", $sChangeInfo))
		{

			if ( $sChangeLine =~ /^([AUDRM])\s+(.*)$/ )
			{
			
				$sChangeType = $1;
				$sFile = $2;

				if( $sChangeType =~ "A" )
				{
					$sPrev = 0;
				}
				else
				{
					$sPrev = $ARGV[0] - 1;
				}
				$sNew = $ARGV[0];

				if ( $ixBug > 0 )
				{
					if ($wget)
					{
						print "Using wget \n";
						my $url = $BUGZ_URL_FINAL.$CVSSUBMIT."?ixBug=".$ixBug."&sFile=".escape($sFile)."&sPrev=".$sPrev."&sNew=".$sNew.$sTrialClause;
						system("$wget_path --no-check-certificate '$url' -q -O /dev/null");
						print "url: ".$url."\n";
					}
					else
					{
						print "Using GET \n";
						my $get = "GET ".$BUGZ_URL_FINAL.$CVSSUBMIT."?ixBug=".$ixBug."&sFile=". escape($sFile)."&sPrev=".$sPrev."&sNew=".$sNew.$sTrialClause."\n\n";
						my $in_addr = (gethostbyname($BUGZ_SERVER))[4] || die("Error: $!\n");
						my $paddr = sockaddr_in($BUGZ_PORT, $in_addr) || die("Error: $!\n");
						socket(S, PF_INET, SOCK_STREAM, getprotobyname('tcp')) || die("Error: $!\n");
						connect(S, $paddr) || die("Error: $!\n");
						select(S);
						$|=1;
						select(STDOUT);
						print S $get;
						close(S);
					}
				}
			}
		}
	}
}
