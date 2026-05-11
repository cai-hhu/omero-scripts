from sre_constants import IN

import omero
import omero.cli
from omero.sys import Parameters
from omero.rtypes import rlong, rlist, rstring, unwrap
import math
import omero.scripts as scripts
from omero.gateway import BlitzGateway

VERSION = "1.0.0"
AUTHORS = ["Tom Boissonnet"]
INSTITUTIONS = ["Heinrich Heine Universitat"]
CONTACT = "tom.boissonnet@hhu.de"

UNIT_D = {
    "mm": "millimeter",
    "um": "micrometer",
    "nm": "nanometer"
}

def process_scalebars(conn, client, script_params):
    qs = conn.getQueryService()
    service_opts = conn.SERVICE_OPTS.copy()

    query = """
        SELECT i.id, s.x1, s.x2, s.y1, s.y2, s.textValue
        FROM Image i
        JOIN i.rois r
        JOIN r.shapes s
    """
    if script_params["Data_Type"] == "Dataset":
        query += " JOIN i.datasetLinks dl WHERE dl.parent.id IN (:iids)"
    elif script_params["Data_Type"] == "Image":
        query += " WHERE i.id IN (:iids)"
    else:
        raise ValueError("Unsupported Data_Type: " + script_params["Data_Type"])

    query += """
        AND s.textValue like 'scalebar:%'
        AND s.class = ome.model.roi.Line
    """

    params = Parameters()
    params.map = {"iids": rlist(map(rlong, script_params["IDs"]))}

    res = qs.projection(query, params, service_opts)
    for row in res:
        img_id, x1, x2, y1, y2, name = map(unwrap, row)

        len_scale = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        _, num, unit = name.split(":")
        px_size = str(float(num) / len_scale)

        args = [
            "metadata", "pixelsize", f"Image:{img_id}",
            "--x", px_size, "--y", px_size, "--unit", UNIT_D[unit]
        ]
        print(" ".join(args))

        cli_ = omero.cli.CLI()
        cli_.loadplugins()
        cli_.set_client(client.createClient(secure=False))
        cli_.invoke(args)
        cli_.get_client().closeSession()

def run_script():
    """
    The main entry point of the script, as called by the client via the
    scripting service, passing the required parameters.
    """
    data_types = [rstring('Dataset'), rstring('Screen')]
    client = scripts.client(
        'Pixelsize_from_scalebar.py',
        f"""
        Change the pixel size of images based on a scale bar ROI.\n
        The image need a line ROI with it's name set as:
        scalebar:<scalebar_length>:<unit>, for example scalebar:100:mm
        to set the pixel size to (100 mm / length) of the line ROI in pixels.\n
        Supported units are mm, um and nm.
        """,
        scripts.String(
            "Data_Type", optional=False, grouping="1",
            description="Image to update individual images, or datasets to"+
            " update all the images it contains.", values=data_types,
            default="Dataset"),
        scripts.List(
            "IDs", optional=False, grouping="1.1",
            description="The images IDs or the dataset IDs containing the " +
            "images to update.").ofType(rlong(0)),
        namespaces=[omero.constants.namespaces.NSDYNAMIC],
        version=VERSION,
        authors=AUTHORS,
        institutions=INSTITUTIONS,
        contact=CONTACT
        )

    try:
        params = client.getInputs(unwrap=True)
        conn = BlitzGateway(client_obj=client)
        conn.c.enableKeepAlive(60)

        print("\n\n################## Script parameters ##################\n")
        print(f"Target: {params['Data_Type']}:{params['IDs']}\n")
        process_scalebars(conn, client, params)

        client.setOutput("Message", rstring("Pixel size updated successfully"))

    except AssertionError as err:
        client.setOutput("ERROR", rstring(err))
        raise AssertionError(str(err))
    except ValueError as err:
        client.setOutput("ERROR", rstring(err))
        raise err
    except Exception as err:
        client.setOutput("ERROR", rstring("An error occured"))
        raise err
    finally:
        client.closeSession()


if __name__ == "__main__":
    run_script()
