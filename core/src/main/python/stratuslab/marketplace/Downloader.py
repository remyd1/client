#
# Created as part of the StratusLab project (http://stratuslab.eu),
# co-funded by the European Commission under the Grant Agreement
# INFSO-RI-261552."
#
# Copyright (c) 2011, SixSq Sarl
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import shutil
import tempfile
import urllib2
import hashlib
from stratuslab.Exceptions import ExecutionException
from stratuslab.ManifestInfo import ManifestInfo

try:
    from lxml import etree
except ImportError:
    try:
        # Python 2.5
        import xml.etree.cElementTree as etree
    except ImportError:
        try:
            # Python 2.5
            import xml.etree.ElementTree as etree
        except ImportError:
            try:
                # normal cElementTree install
                import cElementTree as etree
            except ImportError:
                try:
                    # normal ElementTree install
                    import elementtree.ElementTree as etree
                except ImportError:
                    raise Exception("Failed to import ElementTree from any known place")

from stratuslab import Util
from stratuslab.Signator import Signator
from stratuslab.Compressor import Compressor
from stratuslab.ConfigHolder import ConfigHolder
from stratuslab.Exceptions import InputException
from stratuslab.Exceptions import ValidationException

class Downloader(object):

    ENDPOINT = 'http://appliances.stratuslab.eu/marketplace/metadata'
    LOCAL_IMAGE_FILENAME = '/tmp/image.img'

    def __init__(self, configHolder=ConfigHolder()):
        self.localImageFilename = ''
        self.configHolder = configHolder
        self.imageUrl = None
        configHolder.assign(self)
        self.compression = None
        self.localImageFilename = os.path.abspath(self.localImageFilename)

    def _getManifest(self, imageId, tempMetadataFilename):
        url = self.constructManifestUrl(imageId)
        return self.__getManifest(url, tempMetadataFilename)

    def __getManifest(self, url, tempMetadataFilename):
        try:
            self._download(url, tempMetadataFilename)
        except urllib2.HTTPError:
            raise InputException('Failed to find metadata entry: %s' % url)
        manifestInfo = ManifestInfo(self.configHolder)
        manifestInfo.parseManifestFromFile(tempMetadataFilename)
        return manifestInfo

    def getImageLocations(self, imageId):
        tempMetadataFilename = tempfile.mktemp()
        try:
            locations = [self._getManifest(imageId, tempMetadataFilename).location]
            return locations
        finally:
            try:
                os.unlink(tempMetadataFilename)
            except:
                pass

    def download(self, uri):
        url = self.constructManifestUrl(uri)

        tempMetadataFilename = tempfile.mktemp()

        manifestInfo = self._getManifest(url, tempMetadataFilename)

        locations = [manifestInfo.location]

        tempImageFilename = ''
        for location in locations:
            self._printDetail('Looking for image: %s' % location)
            try:
                tempImageFilename = self._downloadImage(location)
                break
            except:
                pass

        if not os.path.exists(tempImageFilename):
            raise InputException('Failed to find image matching metadata: %s' % url)

        self._verifySignature(tempImageFilename, tempMetadataFilename)

        tempImageFilename = self._inflateImage(tempImageFilename)

        self._verifyHash(tempImageFilename, manifestInfo.sha1)

        shutil.copy2(tempImageFilename, self.localImageFilename)

        os.remove(tempImageFilename)
        os.remove(tempMetadataFilename)

        return self.localImageFilename

    def constructManifestUrl(self, uri):
        endpoint = Util.constructEndPoint(self.endpoint, 'http', '80', 'images')
        url = endpoint + '/' + uri
        return url

    def _loadDom(self, filename):
        file = open(filename).read()
        dom = etree.fromstring(file)
        return dom

    def _downloadImage(self, url):
        compressionExtension = self._extractCompressionExtension(url)

        localFilename = tempfile.mktemp()
        localImageName = localFilename + compressionExtension

        Util.wget(url, localImageName)

        return localImageName

    def _extractCompressionExtension(self, url):
        compression = url.split('.')[-1]

        if compression in ('gz', 'bz2'):
            return '.' + compression
        else:
            return ''

    def _download(self, url, localFilename):
        try:
            return Util.wget(url, localFilename)
        except urllib2.URLError, ex:
            raise InputException('Failed to download: %s, with detail: %s' % (url, str(ex)))

    def _verifySignature(self, imageFilename, metadataFilename):
        signator = Signator(metadataFilename, self.configHolder)
        res = signator.validate()
        if res:
            raise ExecutionException('Failed to validate metadata file')

    def _inflateImage(self, imageFilename):
        extension = self._extractCompressionExtension(imageFilename)
        inflatedFilename = imageFilename
        if extension:
            self._printDetail('Inflating image %s' % imageFilename)
            Compressor.inflate(imageFilename)
            inflatedFilename = imageFilename[: - len(extension)]

        return inflatedFilename

    def _verifyHash(self, imageFilename, hashFromManifest):

        data = open(imageFilename).read()
        sha1 = hashlib.sha1()
        sha1.update(data)

        imageHash = sha1.hexdigest()

        if imageHash != hashFromManifest:
            raise ValidationException('Manifest hash code different from downloaded image: image=%s, matadata=%s' % (imageHash, hashFromManifest))

    def _printDetail(self, message):
        Util.printDetail(message, self.verboseLevel, 1)

