<?xml version="1.0" encoding="iso-8859-1"?>

<resource schema="rob_spoca_ch">
  <meta name="title">SPoCA Coronal Hole</meta>
  <meta name="creationDate">2022-10-10T09:40:00Z</meta>
  <meta name="description" format="plain">
    *** SPoCA Coronal Hole  ***
    TBD
  </meta>
  <meta name="copyright">This research has been made at the Royal Observatory of Belgium</meta>
  <meta name="publisher">SIDC: Solar Influences Data analysis Center</meta>
  <meta name="creator.name">Freek Verstringe</meta>
  <meta name="contact.name">Veronique Delouille</meta>
  <meta name="contact.email">sidc-support@oma.be</meta>
  <meta name="contact.address">Royal Observatory of Belgium, Avenue circulaire 3, 1180 Bruxelles, BELGIQUE</meta>
  <meta name="contributor.name">Benjamin Mampaey</meta>
  <meta name="subject">Sun</meta>
  <meta name="subject">Atmosphere</meta>
  <meta name="contentLevel">General</meta>
  <meta name="contentLevel">University</meta>
  <meta name="contentLevel">Research</meta>
  <meta name="utype">ivo://vopdc.obspm/std/EpnCore#schema-2.0</meta>
  

  <table id="epn_core" onDisk="True" adql="True" primary="granule_uid" forceUnique="True" dupePolicy="overwrite">
    <mixin spatial_frame_type="body"
           optional_columns="access_url access_format access_estsize ">//epntap2#table-2_0</mixin>
           <meta name="description">SPoCA coronal holes</meta>
    <column
      name="observer_lon"
      type="double precision"
      unit="deg"
      description="Observer's Heliographic longitude"
      ucd="obs.observer;pos.bodyrc.lon"
      required="False"
    />
    <column
      name="observer_lat"
      type="double precision"
      unit="deg"
      description="Observer's Heliographic latitude"
      ucd="obs.observer;pos.bodyrc.lat"
      required="False"
    />
    <column
      name="ch_c1_centroid"
      type="double precision"
      unit="deg"
      description="Helioprojective longitude of the centroid of the coronal hole"
      ucd="pos.eq.ra;pos.centroid"
      required="False"
    />
    <column
      name="ch_c2_centroid"
      type="double precision"
      unit="deg"
      description="Helioprojective loatitude of the centroid of the coronal hole"
      ucd="pos.eq.dec;pos.centroid"
      required="False"
    />
    <column
      name="ch_area_projected"
      type="double precision"
      unit="arcsec**2"
      description="Area of the coronal hole as seen by the observer"
      ucd="phys.area"
      required="False"
    />
    <column
      name="ch_area_projected_error"
      type="double precision"
      unit="arcsec**2"
      description="Uncertainety of the area of the coronal hole as seen by the observer"
      ucd="stat.error;phys.area"
      required="False"
    />
    <column
      name="ch_area_deprojected"
      type="double precision"
      unit="km**2"
      description="Estimation of the area of the coronal hole on the solar photosphere"
      ucd="phys.area"
      required="False"
    />
    <column
      name="ch_area_deprojected_error"
      type="double precision"
      unit="km**2"
      description="Uncertainety of the estimation of the area of the coronal hole on the solar photosphere"
      ucd="stat.error;phys.area"
      required="False"
    />
    <column
      name="ch_area_pixels"
      type="integer"
      unit="pix"
      description="Number of pixels of the coronal hole in the map"
      ucd="phys.area;instr.pixel"
      required="False"
    ><values nullLiteral="-9999"/></column>
    <column
      name="ch_stat_aia_image"
      type="text"
      description="Image onto which the coronal hole statistics are computed"
      ucd="meta.id;obs.image"
      required="False"
    />
    <column
      name="ch_stat_aia_sample_size"
      type="integer"
      unit="pix"
      description="Number of pixels of the cornal hole used to compute the statistics, the statistics are computed up to 0.95 solar radius"
      ucd="meta.number;instr.pixel"
      required="True"
    />
    <column
      name="ch_stat_aia_max"
      type="double precision"
      unit="count.s**-1"
      description="Maximum of pixels values of the coronal hole"
      ucd="phot.count;stat.max"
      required="False"
    />
    <column
      name="ch_stat_aia_min"
      type="double precision"
      unit="count.s**-1"
      description="Minimum of pixels values of the coronal hole"
      ucd="phot.count;stat.min"
      required="False"
    />
    <column
      name="ch_stat_aia_median"
      type="double precision"
      unit="count.s**-1"
      description="Median of pixels values of the coronal hole"
      ucd="phot.count;stat.median"
      required="False"
    />
    <column
      name="ch_stat_aia_mean"
      type="double precision"
      unit="count.s**-1"
      description="Mean of pixels values of the coronal hole"
      ucd="phot.count;stat.mean"
      required="False"
    />
    <column
      name="ch_stat_aia_variance"
      type="double precision"
      unit="count**2.s**-2"
      description="Variance of pixels values of the coronal hole"
      ucd="stat.variance;phot.count"
      required="False"
    />
    <column
      name="ch_stat_aia_skewness"
      type="double precision"
      description="Skewness of pixels values of the coronal hole"
      ucd="stat.skewness;phot.count"
      required="False"
    />
    <column
      name="ch_stat_aia_kurtosis"
      type="double precision"
      description="Kurtosis of pixels values of the coronal hole"
      ucd="stat.kurtosis;phot.count"
      required="False"
    />
    <column
      name="ch_stat_aia_first_quartile"
      type="double precision"
      unit="count.s**-1"
      description="First quartile of pixels values of the coronal hole"
      ucd="stat.rank;phot.count"
      required="False"
    />
    <column
      name="ch_stat_aia_third_quartile"
      type="double precision"
      unit="count.s"
      description="Third quartile of pixels values of the coronal hole"
      ucd="stat.rank;phot.count"
      required="False"
    />
    <column
      name="ch_stat_hmi_image"
      type="unicode"
      description="Image onto which the coronal hole statistics are computed"
      ucd="meta.id;obs.image"
      required="False"
    />
    <column
      name="ch_stat_hmi_sample_size"
      type="integer"
      unit="pix"
      description="Number of pixels of the coronal hole used to compute the statistics, the statistics are computed up to 0.95 solar radius"
      ucd="meta.number;instr.pixel"
      required="False"
    />
    <column
      name="ch_stat_hmi_max"
      type="double precision"
      unit="G"
      description="Maximum of the magnetic field of the coronal hole"
      ucd="phys.magField;stat.max"
      required="False"
    />
    <column
      name="ch_stat_hmi_min"
      type="double precision"
      unit="G"
      description="Minimum of the magnetic field of the coronal hole"
      ucd="phys.magField;stat.min"
      required="False"
    />
    <column
      name="ch_stat_hmi_median"
      type="double precision"
      unit="G"
      description="Median of the magnetic field of the coronal hole"
      ucd="phys.magField;stat.median"
      required="False"
    />
    <column
      name="ch_stat_hmi_mean"
      type="double precision"
      unit="G"
      description="Mean of the magnetic field of the coronal hole"
      ucd="phys.magField;stat.mean"
      required="False"
    />
    <column
      name="ch_stat_hmi_variance"
      type="double precision"
      unit="G**2"
      description="Variance of the magnetic field of the coronal hole"
      ucd="stat.variance;phys.magField"
      required="False"
    />
    <column
      name="ch_stat_hmi_skewness"
      type="double precision"
      description="Skewness of the magnetic field of the coronal hole"
      ucd="stat.skewness;phys.magField"
      required="False"
    />
    <column
      name="ch_stat_hmi_kurtosis"
      type="double precision"
      description="Kurtosis of the magnetic field of the coronal hole"
      ucd="stat.kurtosis;phys.magField"
      required="False"
    />
    <column
      name="ch_stat_hmi_first_quartile"
      type="double precision"
      unit="G"
      description="First quartile of the magnetic field of the coronal hole"
      ucd="stat.rank;phys.magField"
      required="False"
    />
    <column
      name="ch_stat_hmi_third_quartile"
      type="double precision"
      unit="G"
      description="Third quartile of the magnetic field of the coronal hole"
      ucd="stat.rank;phys.magField"
      required="False"
    />
		<meta name="_associatedDatalinkService">
			<meta name="serviceId">dl</meta>
			<meta name="idColumn">granule_uid</meta>
		</meta>
  </table>

  <data id="import">
    <sources pattern="data/ch/*.csv"/>
    <csvGrammar>
    </csvGrammar>
		<make table="epn_core">
			<rowmaker idmaps='*'>
      <map dest="access_estsize">round(parseWithNull(@access_estsize, float, "-9999"))</map>
			</rowmaker>
		</make>
  </data>
  
  <table id="tracking" onDisk="True" adql="True" primary="previous,next" forceUnique="True" dupePolicy="overwrite">
           <meta name="description">SPoCA coronal holes tracking</meta>
    <column
      name="previous"
      type="text"
      description="The granule_uid of the detection"
      ucd="meta.id"
      required="False"
    />
    <column
      name="quoted/next"
      type="text"
      description="The granule_uid of the detection"
      ucd="meta.id"
      required="false"
    />
    <column
      name="overlap_area_projected"
      type="double precision"
      unit="arcsec**2"
      description="Size of the overlap between the 2 detections"
      ucd="phys.area"
      required="false"
    />
    <column
      name="overlap_area_pixels"
      type="double precision"
      unit="pix"
      description="Size of the overlap between the 2 detections"
      ucd="phys.area;instr.pixel"
      required="false"
    ><values nullLiteral="-9999"/></column>
  </table>

  <data id="import_tracking">
    <sources pattern="data/ch_tracking/*.csv"/>
    <csvGrammar>
    </csvGrammar>
		<make table="tracking">
			<rowmaker idmaps='*'>
			</rowmaker>
		</make>
  </data>

  <table id="datalink" onDisk="True" adql="True" primary="granule_uid" forceUnique="True" dupePolicy="overwrite">
           <meta name="description">SPoCA coronal holes datalink</meta>
    <column
      name="granule_uid"
      type="text"
      description="The granule_uid of the detection"
      ucd="meta.id"
      required="False"
    />
    <column
      name="thumbnail_url"
      type="text"
      description="URL of a thumbnail image"
      ucd="meta.ref.url"
      required="False"
    />
    <column
      name="ch_stat_aia_image_url"
      type="text"
      description="URL of the AIA image onto which the coronal hole statistics are computed"
      ucd="meta.ref.url"
      required="False"
    />
    <column
      name="ch_stat_hmi_image_url"
      type="text"
      description="URL of the HMI image onto which the coronal hole statistics are computed"
      ucd="meta.ref.url"
      required="False"
    />
    <column
      name="provenance_url"
      type="text"
      description="URL of the provenance file for the coronal hole map"
      ucd="meta.ref.url"
      required="False"
    />
  </table>

  <data id="import_dl">
    <sources pattern="data/ch/*.csv"/>
    <csvGrammar>
    </csvGrammar>
		<make table="datalink">
			<rowmaker idmaps='*'>
			</rowmaker>
		</make>
  </data>


	<service id="dl" allowed="dlmeta">
		<meta name="title">ROB SPoCA coronal hole datalink service</meta>
		<datalinkCore>
			<metaMaker semantics="#thumbnail">
				<code>
					yield descriptor.makeLink(descriptor.metadata['thumbnail_url'], description="PNG Thumbnail", contentType='image/png')
				</code>
			</metaMaker>
			<descriptorGenerator>
				<code>
					granule_uid = pubDID.split("?", 1)[-1]
					desc = ProductDescriptor.fromAccref(pubDID, accref)

					with base.getTableConn() as conn:
						desc.metadata = list(
							conn.queryToDicts(
								"SELECT * FROM \schema.datalink WHERE granule_uid=%(uid)s", {"uid": accref}
							)
						)[0]
					return desc
				</code>
			</descriptorGenerator>

		</datalinkCore>
	</service>
  <service id="spoca_ch_dr" allowed="form,static">
    <meta name="shortName">CH service</meta>
    <meta name="title">CH service title</meta>
    <publish render="form" sets="local"/>
    <dbCore queriedTable="epn_core"></dbCore>
    <meta name="_example" title="tap_schema example">
			This example lists SPoCA coronal hole detections.

			.. tapquery::

				SELECT * FROM rob_spoca_ch.epn_core LIMIT 10
    </meta>
  </service>
</resource>
