/**
 * @param {string} str
 * @param {number} len
 * @param {string} char
 * @returns {string}
 */
function lpad(str, len, char) {
    while (str.length < len) { str = char + str; } return str;
};

/**
 * @param {string} str
 * @param {number} len
 * @param {string} char
 * @returns {string}
 */
function rpad(str, len, char) {
    while (str.length < len) { str = str + char; } return str;
};

/**
 * @param {object} view
 * @param {number} fieldLength
 * @param {string} str
 * @param {number} offset
 * @returns {number}
 */
function writeField(view, fieldLength, str, offset) {
    for (var i = 0; i < fieldLength; i++) {
        view.setUint8(offset, str.charCodeAt(i)); offset++;
    }
    return offset;
};

var types = {
    string: 'C',
    number: 'N',
    boolean: 'L',
    // type to use if all values of a field are null
    null: 'C'
};


function multi(features) {
    var fields = {};
    features.forEach(collect);
    function collect(f) { inherit(fields, f); }
    return obj(fields);
}

/**
 * @param {Object} a
 * @param {Object} b
 * @returns {Object}
 */
function inherit(a, b) {
    for (var i in b) {
        var isDef = typeof b[i] !== 'undefined' && b[i] !== null;
        if (typeof a[i] === 'undefined' || isDef) {
          a[i] = b[i];
        }
    }
    return a;
}

var fieldSize = {
    // string
    C: 254,
    // boolean
    L: 1,
    // date
    D: 8,
    // number
    N: 18,
    // number
    M: 18,
    // number, float
    F: 18,
    // number
    B: 8,
};

function obj(_) {
    var fields = {}, o = [];
    for (var p in _) fields[p] = _[p] === null ? 'null' : typeof _[p];
    for (var n in fields) {
        var t = types[fields[n]];
        if(t){
             o.push({
                name: n,
                type: t,
                size: fieldSize[t]
            });
        }
    }
    return o;
}

/**
 * @param {Array} fields
 * @returns {Array}
 */
function bytesPer(fields) {
    // deleted flag
    return fields.reduce(function(memo, f) { return memo + f.size; }, 1);
}


function structuredbf(data, meta) {

    var field_meta = meta || multi(data),
        fieldDescLength = (32 * field_meta.length) + 1,
        bytesPerRecord = bytesPer(field_meta), // deleted flag
        buffer = new ArrayBuffer(
            // field header
            fieldDescLength +
            // header
            32 +
            // contents
            (bytesPerRecord * data.length) +
            // EOF marker
            1
    ),
        now = new Date(),
        view = new DataView(buffer);

    // version number - dBase III
    view.setUint8(0, 0x03);
    // date of last update
    view.setUint8(1, now.getFullYear() - 1900);
    view.setUint8(2, now.getMonth());
    view.setUint8(3, now.getDate());
    // number of records
    view.setUint32(4, data.length, true);

    // length of header
    var headerLength = fieldDescLength + 32;
    view.setUint16(8, headerLength, true);
    // length of each record
    view.setUint16(10, bytesPerRecord, true);

    // Terminator
    view.setInt8(32 + fieldDescLength - 1, 0x0D);

    field_meta.forEach(function(f, i) {
        // field name
        f.name.split('').slice(0, 8).forEach(function(c, x) {
            view.setInt8(32 + i * 32 + x, c.charCodeAt(0));
        });
        // field type
        view.setInt8(32 + i * 32 + 11, f.type.charCodeAt(0));
        // field length
        view.setInt8(32 + i * 32 + 16, f.size);
        if (f.type == 'N') view.setInt8(32 + i * 32 + 17, 3);
    });

    offset = fieldDescLength + 32;

    data.forEach(function(row, num) {
        // delete flag: this is not deleted
        view.setUint8(offset, 32);
        offset++;
        field_meta.forEach(function(f) {
            var val = row[f.name];
            if (val === null || typeof val === 'undefined') val = '';

            switch (f.type) {
                // boolean
                case 'L':
                    view.setUint8(offset, val ? 84 : 70);
                    offset++;
                    break;

                // date
                case 'D':
                    offset = writeField(view, 8,
                        lpad(val.toString(), 8, ' '), offset);
                    break;

                // number
                case 'N':
                    offset = writeField(view, f.size,
                        lpad(val.toString(), f.size, ' ').substr(0, 18),
                        offset);
                    break;

                // string
                case 'C':
                    offset = writeField(view, f.size,
                        rpad(val.toString(), f.size, ' '), offset);
                    break;

                default:
                    throw new Error('Unknown field type');
            }
        });
    });

    // EOF flag
    view.setUint8(offset, 0x1A);

    return view;
};






//-------------------------------------------------------------

geojsonpoint = justType('Point', 'POINT');
geojsonline = justType('LineString', 'POLYLINE');
geojsonpolygon = justType('Polygon', 'POLYGON');

function justType(type, TYPE) {
    return function(gj) {
        var oftype = gj.features.filter(isType(type));
        return {
            geometries: (TYPE === 'POLYGON' || TYPE === 'POLYLINE') ? [oftype.map(justCoords)] : oftype.map(justCoords),
            properties: oftype.map(justProps),
            type: TYPE
        };
    };
}

function justCoords(t) {
	//console.log(t);
	if (t.geometry === undefined) return [];
    if (t.geometry.coordinates[0] !== undefined &&
        t.geometry.coordinates[0][0] !== undefined &&
        t.geometry.coordinates[0][0][0] !== undefined) {
        return t.geometry.coordinates[0];
    } else {
		
        return t.geometry.coordinates;
    }
}

function justProps(t) {
    return t.properties;
}

function isType(t) {
    return function(f) { return f.geometry.type === t; };
}

//------------------------------------------------------------

var 
	//types = require('./types'),
    //dbf = require('dbf'),
    //prj = require('./prj'),
	prj = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]]'
    //ext = require('./extent'),
    //getFields = require('./fields'),
    //assert = require('assert'),
    //pointWriter = require('./points'),
    //polyWriter = require('./poly');
/*
var writers = {
    1: pointWriter,
    5: polyWriter,
    3: polyWriter
};
*/
var recordHeaderLength = 8;


// Low-level writing interface
function writePoint(rows, geometry_type, geometries, callback) {
	
	
	parts = function parts(geometries, TYPE) {
		return geometries.length;
	};
	
	shxLength = function(coordinates) {
		
			return coordinates.length * 8;
	};
	
	shpLength = function(coordinates) {
		return coordinates.length * 28;
	};
	
	extenlarge = function enlargeExtent(extent, pt) {
		if (pt[0] < extent.xmin) extent.xmin = pt[0];
		if (pt[0] > extent.xmax) extent.xmax = pt[0];
		if (pt[1] < extent.ymin) extent.ymin = pt[1];
		if (pt[1] > extent.ymax) extent.ymax = pt[1];
		return extent;
	};

	extenlargeExtent = function enlargeExtent(extent, ext) {
		if (ext.xmax > extent.xmax) extent.xmax = ext.xmax;
		if (ext.xmin < extent.xmin) extent.xmin = ext.xmin;
		if (ext.ymax > extent.ymax) extent.ymax = ext.ymax;
		if (ext.ymin < extent.ymin) extent.ymin = ext.ymin;
		return extent;
	};
	
	extblank = function() {
		return {
			xmin: Number.MAX_VALUE,
			ymin: Number.MAX_VALUE,
			xmax: -Number.MAX_VALUE,
			ymax: -Number.MAX_VALUE
		};
	};
	
	extent = function(coordinates) {
		return coordinates.reduce(function(extent, coords) {
			return extenlarge(extent, coords);
		}, extblank());
	};
	
	 var TYPE = typesgeometries[geometry_type],
      //  writer = writers[TYPE],
        parts = parts(geometries, TYPE),
        shpLength = 100 + (parts - geometries.length) * 4 + shpLength(geometries),
        shxLength = 100 + shxLength(geometries),
        shpBuffer = new ArrayBuffer(shpLength),
        shpView = new DataView(shpBuffer),
        shxBuffer = new ArrayBuffer(shxLength),
        shxView = new DataView(shxBuffer),
        extent = extent(geometries);

    writeHeader(shpView, TYPE);
    writeHeader(shxView, TYPE);
    writeExtent(extent, shpView);
    writeExtent(extent, shxView);

    writePoints2(geometries, extent,
        new DataView(shpBuffer, 100),
        new DataView(shxBuffer, 100),
        TYPE);

    shpView.setInt32(24, shpLength / 2);
    shxView.setInt32(24, (50 + geometries.length * 4));

    var dbfBuf = structuredbf(rows);

    callback(null, {
        shp: shpView,
        shx: shxView,
        dbf: dbfBuf,
        prj: prj
    });
}

function writePoints2(coordinates, extent, shpView, shxView) {

    var contentLength = 28, // 8 header, 20 content
        fileLength = 100,
        shpI = 0,
        shxI = 0;
	//console.log(coordinates)
    coordinates.forEach(function writePoint(coords, i) {
		//console.log(coords)
		//console.log(i)
        // HEADER
        // 4 record number
        // 4 content length in 16-bit words (20/2)
        shpView.setInt32(shpI, i);
        shpView.setInt32(shpI + 4, 10);

        // record
        // (8 + 8) + 4 = 20 content length
        shpView.setInt32(shpI + 8, 1, true); // POINT=1
        shpView.setFloat64(shpI + 12, coords[0], true); // X
        shpView.setFloat64(shpI + 20, coords[1], true); // Y

        // index
        shxView.setInt32(shxI, fileLength / 2); // length in 16-bit words
        shxView.setInt32(shxI + 4, 10);

        shxI += 8;
        shpI += contentLength;
        fileLength += contentLength;
    });
};









function writeNonPoints(rows, geometry_type, geometries, callback) {
	
	//console.log('1')
	function parts(geometries, TYPE) {
		var no = 1;
		
		if (TYPE === typesgeometries.POLYGON || TYPE === typesgeometries.POLYLINE)  {
			no = geometries.reduce(function (no, coords) {
				no += coords.length;
				if (Array.isArray(coords[0][0][0])) { // multi
					no += coords.reduce(function (no, rings) {
						return no + rings.length - 1; // minus outer
					}, 0);
				}
				return no;
			}, 0);
		}
		return no;
	}
	
	shxLength = function(geometries) {
		return geometries.length * 8;
	};
	
	shpLength = function(geometries) {
		return (geometries.length * 56) +
			// points
			(justCoords(geometries).length * 16);
	};
	
	extenlarge = function enlargeExtent(extent, pt) {
		if (pt[0] < extent.xmin) extent.xmin = pt[0];
		if (pt[0] > extent.xmax) extent.xmax = pt[0];
		if (pt[1] < extent.ymin) extent.ymin = pt[1];
		if (pt[1] > extent.ymax) extent.ymax = pt[1];
		return extent;
	};

	extenlargeExtent = function enlargeExtent(extent, ext) {
		if (ext.xmax > extent.xmax) extent.xmax = ext.xmax;
		if (ext.xmin < extent.xmin) extent.xmin = ext.xmin;
		if (ext.ymax > extent.ymax) extent.ymax = ext.ymax;
		if (ext.ymin < extent.ymin) extent.ymin = ext.ymin;
		return extent;
	};
	
	extblank = function() {
		return {
			xmin: Number.MAX_VALUE,
			ymin: Number.MAX_VALUE,
			xmax: -Number.MAX_VALUE,
			ymax: -Number.MAX_VALUE
		};
	};
	
	extent = function(coordinates) {
		return justCoords(coordinates).reduce(function(extent, c) {
			return extenlarge(extent, c);
		}, extblank());
	};
	
	function justCoords(coords, l) {
		if (l === undefined) l = [];
		if (typeof coords[0][0] == 'object') {
			return coords.reduce(function(memo, c) {
				return memo.concat(justCoords(c));
			}, l);
		} else {
			return coords;
		}
	}
	
	//if (geometries.length > 1)
	//console.log(geometries.length)
	//console.log(geometries[0].length)
	if (geometries.length == 1)
		geometries = geometries[0]
	
	 var TYPE = typesgeometries[geometry_type],
      //  writer = writers[TYPE],
        parts = parts(geometries, TYPE),
        shpLength = 100 + (parts - geometries.length) * 4 + shpLength(geometries),
        shxLength = 100 + shxLength(geometries),
        shpBuffer = new ArrayBuffer(shpLength),
        shpView = new DataView(shpBuffer),
        shxBuffer = new ArrayBuffer(shxLength),
        shxView = new DataView(shxBuffer),
        extent = extent(geometries);
	/*console.log(TYPE);
	console.log(parts);
	console.log(shpLength);
	console.log(shxLength);
	console.log(extent);
	*/
    writeHeader(shpView, TYPE);
    writeHeader(shxView, TYPE);
    writeExtent(extent, shpView);
    writeExtent(extent, shxView);

    writeNonPoints2(geometries, extent,
        new DataView(shpBuffer, 100),
        new DataView(shxBuffer, 100),
        TYPE);

    shpView.setInt32(24, shpLength / 2);
    shxView.setInt32(24, (50 + geometries.length * 4));

    var dbfBuf = structuredbf(rows);

    callback(null, {
        shp: shpView,
        shx: shxView,
        dbf: dbfBuf,
        prj: prj
    });
}

function writeNonPoints2(geometries, extent, shpView, shxView, TYPE) {
	
	extenlarge = function enlargeExtent(extent, pt) {
		if (pt[0] < extent.xmin) extent.xmin = pt[0];
		if (pt[0] > extent.xmax) extent.xmax = pt[0];
		if (pt[1] < extent.ymin) extent.ymin = pt[1];
		if (pt[1] > extent.ymax) extent.ymax = pt[1];
		return extent;
	};
	
	extenlargeExtent = function enlargeExtent(extent, ext) {
		if (ext.xmax > extent.xmax) extent.xmax = ext.xmax;
		if (ext.xmin < extent.xmin) extent.xmin = ext.xmin;
		if (ext.ymax > extent.ymax) extent.ymax = ext.ymax;
		if (ext.ymin < extent.ymin) extent.ymin = ext.ymin;
		return extent;
	};
	
	extblank = function() {
		return {
			xmin: Number.MAX_VALUE,
			ymin: Number.MAX_VALUE,
			xmax: -Number.MAX_VALUE,
			ymax: -Number.MAX_VALUE
		};
	};
	
	function parts(geometries, TYPE) {
		var no = 1;
		if (TYPE === geometries.POLYGON || TYPE === geometries.POLYLINE)  {
			no = geometries.reduce(function (no, coords) {
				no += coords.length;
				if (Array.isArray(coords[0][0][0])) { // multi
					no += coords.reduce(function (no, rings) {
						return no + rings.length - 1; // minus outer
					}, 0);
				}
				return no;
			}, 0);
		}
		return no;
	}

	function justCoords(coords) {
		
		if (typeof coords[0][0] == 'object') {
			return coords.reduce(function(memo, c) {
				return memo.concat(justCoords(c));
			}, l);
		} else {
			return coords;
		}
	}

    var shpI = 0,
        shxI = 0,
        shxOffset = 100;
	
    geometries.forEach(
	
		function writePolyLine(coordinates, i) {
			//console.log(coordinates)
			//console.log(i)
			var flattened = justCoords(coordinates),
				noParts = parts([coordinates], TYPE),
				contentLength = (flattened.length * 16) + 48 + (noParts - 1) * 4;
			
			//console.log(flattened)
			//console.log(noParts)
			//console.log(contentLength)
			
			var featureExtent = flattened.reduce(function(extent, c) {
				return extenlarge(extent, c);
			}, extblank());

			// INDEX
			shxView.setInt32(shxI, shxOffset / 2); // offset
			shxView.setInt32(shxI + 4, contentLength / 2); // offset length

			shxI += 8;
			shxOffset += contentLength + 8;

			shpView.setInt32(shpI, i + 1); // record number
			shpView.setInt32(shpI + 4, contentLength / 2); // length
			shpView.setInt32(shpI + 8, TYPE, true); // POLYLINE=3
			shpView.setFloat64(shpI + 12, featureExtent.xmin, true); // EXTENT
			shpView.setFloat64(shpI + 20, featureExtent.ymin, true);
			shpView.setFloat64(shpI + 28, featureExtent.xmax, true);
			shpView.setFloat64(shpI + 36, featureExtent.ymax, true);
			shpView.setInt32(shpI + 44, noParts, true);
			shpView.setInt32(shpI + 48, flattened.length, true); // POINTS
			shpView.setInt32(shpI + 52, 0, true); // The first part - index zero

			var onlyParts = coordinates.reduce(function (arr, coords) {
				if (Array.isArray(coords[0][0])) {
					arr = arr.concat(coords);
				} else {
					arr.push(coords);
				}
				return arr;
			}, []);
			for (var p = 1; p < noParts; p++) {
				shpView.setInt32( // set part index
					shpI + 52 + (p * 4),
					onlyParts.reduce(function (a, b, idx) {
						return idx < p ? a + b.length : a;
					}, 0),
					true
				);
			}

			flattened.forEach(function writeLine(coords, i) {
				shpView.setFloat64(shpI + 56 + (i * 16) + (noParts - 1) * 4, coords[0], true); // X
				shpView.setFloat64(shpI + 56 + (i * 16) + (noParts - 1) * 4 + 8, coords[1], true); // Y
			});

			shpI += contentLength + 8;
		}
	)
};

function writeHeader(view, TYPE) {
    view.setInt32(0, 9994);
    view.setInt32(28, 1000, true);
    view.setInt32(32, TYPE, true);
}

function writeExtent(extent, view) {
    view.setFloat64(36, extent.xmin, true);
    view.setFloat64(44, extent.ymin, true);
    view.setFloat64(52, extent.xmax, true);
    view.setFloat64(60, extent.ymax, true);
}

//--------------------------------------------------------

typesgeometries = {
    NULL: 0,
    POINT: 1,
    POLYLINE: 3,
    POLYGON: 5,
    MULTIPOINT: 8,
    POINTZ: 11,
    POLYLINEZ: 13,
    POLYGONZ: 15,
    MULTIPOINTZ: 18,
    POINTM: 21,
    POLYLINEM: 23,
    POLYGONM: 25,
    MULTIPOINTM: 28,
    MULTIPATCH: 31,
};


//--------------------------------------------------------

function zip(gj, options){
	var zip = new JSZip(),
        layers = zip.folder(options && options.folder ? options.folder : 'layers');
	[geojsonpoint(gj), geojsonline(gj), geojsonpolygon(gj)]
        .forEach(function(l) {
		
        if (l.geometries.length && l.geometries[0].length) {
			//console.log(l.properties)
			//console.log(l.type)
			
			if (l.type == "POINT")
			{
				
				writePoint(
					// field definitions
					l.properties,
					// geometry type
					l.type,
					// geometries
					l.geometries,
					function(err, files) {
						var fileName = options && options.types[l.type.toLowerCase()] ? options.types[l.type.toLowerCase()] : l.type;
						layers.file(fileName + '.shp', files.shp.buffer, { binary: true });
						layers.file(fileName + '.shx', files.shx.buffer, { binary: true });
						layers.file(fileName + '.dbf', files.dbf.buffer, { binary: true });
						layers.file(fileName + '.prj', prj);
					});
			}
			else
				writeNonPoints(
					// field definitions
					l.properties,
					// geometry type
					l.type,
					// geometries
					l.geometries,
					function(err, files) {
						var fileName = options && options.types[l.type.toLowerCase()] ? options.types[l.type.toLowerCase()] : l.type;
						layers.file(fileName + '.shp', files.shp.buffer, { binary: true });
						layers.file(fileName + '.shx', files.shx.buffer, { binary: true });
						layers.file(fileName + '.dbf', files.dbf.buffer, { binary: true });
						layers.file(fileName + '.prj', prj);
					});
        }
    });

    var generateOptions = { compression:'STORE',type : 'base64' };
/*
    if (!process.browser) {
      generateOptions.type = 'nodebuffer';
    }
*/
    //return zip.generate(generateOptions);
	return zip.generateAsync(generateOptions);
}

function saveAs(uri, filename) {
  var link = document.createElement('a');
  if (typeof link.download === 'string') {
    link.href = uri;
    link.download = filename;

    //Firefox requires the link to be in the body
    document.body.appendChild(link);
    
    //simulate click
    link.click();

    //remove the link when done
    document.body.removeChild(link);
  } else {
    window.open(uri);
  }
}

function downloadShp(gj,options,filename){
	
	zip(gj, options).then(function(content) {
		
		 file = 'data:application/zip;base64,' + content
		 saveAs(file,filename)
	  });
}