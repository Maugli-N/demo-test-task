package to_db;

=Info
  ЃЁЎ«Ё®вҐЄ  ¤«п а Ў®вл б ¤Ґ¬®­бва жЁ®­­®© Ў §®© ¤ ­­ле

  Ђўв®а: N.N.S.
  ‚ҐабЁп ®в: 2024-08-15

  ‘ЇЁб®Є дг­ЄжЁ©
      to_db::connect - Ї®¤Є«озҐ­ЁҐ Є Ў §Ґ ¤ ­­ле
=cut

use strict "vars";
use DBI;

# ”г­ЄжЁп Ї®¤Є«озҐ­Ёп Є Ў §Ґ ¤ ­­ле
sub connect
{
  # ЂваЁЎгвл ¤®бвгЇ  Є Ў §Ґ ¤ ­­ле
  my $host = 'localhost';
  my $base = 'demo_to_go_ru';
  my $user = 'demo-to-go-ru';
  my $pass = 'dEm0~T';
  # ЋЇжЁЁ ­ бва®©ЄЁ Ї®¤Є«озҐ­Ёп Є MySQL
  my $opts = 'mysql_enable_utf8=1';
  # Љ®­дЁЈга жЁп б®Ґ¤Ё­Ґ­Ёп б Ў §®© ¤ ­­ле
  my $dsn = 'DBI:mysql:' . $base . ';' . $host. ';' . $opts;
  # Џа®ЎгҐ¬ Ї®¤Є«озЁвмбп Є Ў §Ґ ¤ ­­ле
  my $dbh = DBI->connect($dsn, $user, $pass, { PrintError => 0 });
  return $dbh;
}

1;