# Tools Background

## HDF5 Filetype

### Use-Case

The HDF5 database file is used for highly efficient storage of large datasets, in this case a logical storage architecture for labeled spectral data generated from the array.

### File Structure

#### HDF5 Implementation

A detailed description of the HDF5 file implementation can be found on [the HDF5 website](https://portal.hdfgroup.org/display/HDF5/Introduction+to+HDF5).

##### Groups

HDF5 Files are structured similar to a UNIX filesystem where `groups` are analagous to `folders` in a UNIX filesystem.

Every HDF5 file has a root `group` labeled `/`.  `Sub-groups` can be added to this root `group` and nested as deeply as desired `/foo/bar`.

##### Datasets

`Datasets` are data objects that may be stored in `groups`.  Each `dataset` may contian metadata (such as sample size, sample rate, etc.) as well as data itself.

##### Dataspaces

`Dataspaces` describe the layout of the data in a dataset.

##### Datatypes

`Datatypes` describe the dimension of each data being stored.

A helpful graphic to visualize the relation between `Dataspaces` and `Datatypes` (from the HDF website) is included below:
![](https://portal.hdfgroup.org/download/attachments/50078525/cmpnddtype.png?version=1&modificationDate=1517522158356&api=v2)

In this image the `dataspace` is a 5x3 array, and the `datatype` contains a int16, a char, an int32 and a 2x3x2 aarray of float32.

##### Attributes

`Attributes` are optional metadata stored with HDF5 objects and are stored in a key value pair.  In Python these are accessed similar to a dictionary.  `Attributes` can be applied to any HDF5 data object (`group` and `dataset`).

##### Properties

`Properties` are simply how the data is stored.  The available options are _contiguious(default), chunked,_ or _compressed & chunked_.  `Chunked` is extensible so the dataset may be added onto arbitrarily, while `contiguious` is pre-allocated.
