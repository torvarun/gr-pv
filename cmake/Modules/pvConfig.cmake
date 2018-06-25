INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_PV pv)

FIND_PATH(
    PV_INCLUDE_DIRS
    NAMES pv/api.h
    HINTS $ENV{PV_DIR}/include
        ${PC_PV_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    PV_LIBRARIES
    NAMES gnuradio-pv
    HINTS $ENV{PV_DIR}/lib
        ${PC_PV_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(PV DEFAULT_MSG PV_LIBRARIES PV_INCLUDE_DIRS)
MARK_AS_ADVANCED(PV_LIBRARIES PV_INCLUDE_DIRS)

