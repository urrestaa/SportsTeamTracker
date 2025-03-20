{pkgs}: {
  deps = [
    pkgs.pkg-config
    pkgs.arrow-cpp
    pkgs.sqlite-interactive
    pkgs.glibcLocales
    pkgs.rustc
    pkgs.libiconv
    pkgs.cargo
  ];
}
