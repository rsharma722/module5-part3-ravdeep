const express = require("express");
const { MongoClient } = require("mongodb");

const app = express();
app.use(express.json());

const client = new MongoClient("mongodb://mongo:27017");
let db;

async function connectDB() {
  await client.connect();
  db = client.db("bank_app");
  console.log("Connected to MongoDB");
}

connectDB();

app.get("/api/transactions", async (req, res) => {
  const transactions = await db.collection("transactions").find().toArray();
  res.json(transactions);
});

app.listen(6000, () => {
  console.log("Transactions service running on port 6000");
});