package to_db;

=Info
  Библиотека для работы с демонстрационной базой данных

  Автор: N.N.S.
  Версия от: 2024-08-15

  Список функций
      to_db::connect - подключение к базе данных
=cut

use strict "vars";
use DBI;

# Функция подключения к базе данных
sub connect
{
  # Атрибуты доступа к базе данных
  my $host = 'localhost';
  my $base = 'demo_to_go_ru';
  my $user = 'demo-to-go-ru';
  my $pass = 'dEm0~T';
  # Опции настройки подключения к MySQL
  my $opts = 'mysql_enable_utf8=1';
  # Конфигурация соединения с базой данных
  my $dsn = 'DBI:mysql:' . $base . ';' . $host. ';' . $opts;
  # Пробуем подключиться к базе данных
  my $dbh = DBI->connect($dsn, $user, $pass, { PrintError => 0 });
  return $dbh;
}

1;