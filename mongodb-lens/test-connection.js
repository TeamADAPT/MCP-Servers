import { MongoClient } from 'mongodb';

const uri = "mongodb://admin:nova_secure_password@52.118.145.162:27017/admin?authSource=admin";
const client = new MongoClient(uri, {
  directConnection: true,
  serverSelectionTimeoutMS: 5000
});

async function run() {
  try {
    await client.connect();
    console.log("Connected successfully to MongoDB");
    const adminDb = client.db("admin");
    const result = await adminDb.command({ ping: 1 });
    console.log("Ping result:", result);
  } catch (err) {
    console.error("Connection error:", err);
  } finally {
    await client.close();
  }
}

run();
