import json
from pathlib import Path
import pandas as pd
import geopandas as gp
from shapely.ops import nearest_points


reldir = str(Path.cwd())


def findMaxCluster(radius, fname):
    docList = []
    # radius miles to meters
    radius = radius * 1609.344
    try:
        with open(fname, "r") as dfile:
            # try to load the tidy string as json into list
            docList = json.load(dfile)

    except FileNotFoundError as e:
        print("Failed to open file")
        print(str(e))

    except Exception as e:
        print("Failed to read features from file")
        print(str(e))

    if len(docList) > 1:
        latList = []
        lonList = []
        for item in docList:
            lonList.append(float(item['addresses'][0]['longitude']))
            latList.append(float(item['addresses'][0]['latitude']))
        data = pd.DataFrame({'lon': lonList, 'lat': latList})
        pntsGeom = gp.points_from_xy(data.lon, data.lat)
        crs = {'init': 'epsg:4326'}
        # create all points geodataframe
        points = gp.GeoDataFrame(data, crs=crs, geometry=pntsGeom)

        # cluster results
        results = []

        # loop through each node
        for pidx in range(len(points)):
            # define a cluster
            cluster = gp.GeoSeries()
            # add to the cluster until its outside the radius then break
            while True:
                if len(cluster) > 0:
                    # envelop the last cluster result
                    env = cluster.envelope
                    # get a centroid from that shape
                    cen = env.centroid
                    # find the next point and add it to the cluster
                    nearpoints = nearest_points(cen, points)
                    nextpoint = nearpoints[1]
                    cluster.append(nextpoint)
                    # envelop the current cluster again
                    env = cluster.envelope
                    # get a centroid from that new shape
                    cen = env.centroid()
                    # buffer that centroid with the given radius and make sure
                    bufrad = cen.buffer(radius)
                    # if the buffered area does not contain the node points then add the previous cluster to results and break
                    if not bufrad.contains(points):
                        results.append(cluster)
                        break
                else:
                    cluster.append(points[pidx])

        # take the result cluster with the max points
        maxC = max(c for c in results)
        # envelop max cluster
        env = maxC.envelope
        # get a centroid from that shape
        cen = env.centroid()
        locCord = (round(cen.x, 3), round(cen.y, 3))
        return locCord


if __name__ == '__main__':

    findMaxCluster(5, reldir + '\\carefirst_bluechoice_doctors.json')
