Advanced Research Computing Status Dash App
---

#### Description

Using Slurm data from your compute cluster, the most recent utilization is
shown in a Pie Graph format. Plot updates every 5 minutes with new data being
written every 15 minutes.

This is not meant as an administrative tool, but as an aesthetically pleasing
reference for users to quickly gauge the activity on the various clusters at our
center.

#### Software Resources

- [Dash](https://plot.ly/products/dash/) for plotting and updates on the fly
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) and
  [PyMongo](http://api.mongodb.com/python/current/tutorial.html) for hosting
  and writing/reading to/from MongoDB

#### Data Collection

Example collection scripts can be found at
https://github.com/barrymoo/crc-status-dash
