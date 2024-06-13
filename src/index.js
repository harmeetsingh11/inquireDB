require('dotenv').config(); // Load environment variables from .env
const sqlite3 = require('sqlite3').verbose();
const Groq = require('groq-sdk');

// Initialize Groq with API Key
const groq = new Groq({ apiKey: process.env.GROQ_API_KEY });

// Function to extract schema information from the SQLite3 database
const getSchemaInfo = () => {
  return new Promise((resolve, reject) => {
    const db = new sqlite3.Database('./databases/northwind.db');
    db.serialize(() => {
      db.all(
        "SELECT name FROM sqlite_master WHERE type='table';",
        (err, tables) => {
          if (err) {
            reject(err);
            return;
          }
          const schema = {};
          let pendingTables = tables.length;

          tables.forEach((table) => {
            const tableName = `"${table.name}"`; // Ensure table names with spaces are handled
            db.all(`PRAGMA table_info(${tableName});`, (err, columns) => {
              if (err) {
                reject(err);
                return;
              }
              schema[table.name] = columns.map((column) => column.name);
              pendingTables -= 1;
              if (pendingTables === 0) {
                resolve(schema);
                db.close();
              }
            });
          });
        }
      );
    });
  });
};

// Function to generate SQL query from a plain English question using GroqAPI
const generateSQLQuery = async (question, schema) => {
  const prompt = `
You are a helpful assistant that converts plain English questions into SQL queries.
Make sure the SQL queries match the actual table and column names in the schema provided.
Output only the SQL query without any additional text.

Schema:
${JSON.stringify(schema, null, 2)}

Question: "${question}"
SQL Query:
`;

  const chatCompletion = await groq.chat.completions.create({
    messages: [
      {
        role: 'system',
        content:
          'you are a helpful assistant that converts plain English questions into SQL queries. Output only the SQL query without any additional text.',
      },
      { role: 'user', content: prompt },
    ],
    model: 'llama3-8b-8192',
    temperature: 0.5,
    max_tokens: 1024,
    top_p: 1,
    stop: null,
    stream: false,
  });

  return chatCompletion.choices[0]?.message?.content.trim() || '';
};

// Function to run the generated SQL query on the SQLite3 database and display the results
const runSQLQuery = (query) => {
  return new Promise((resolve, reject) => {
    const db = new sqlite3.Database('./databases/northwind.db');
    db.all(query, (err, rows) => {
      if (err) {
        reject(err);
        return;
      }
      resolve(rows);
      db.close();
    });
  });
};

// Main function to execute the process
const main = async () => {
  try {
    const schema = await getSchemaInfo();
    console.log('Schema extracted from database:', schema);

    const question = 'List the names of all customers who are from USA.';
    const sqlQuery = await generateSQLQuery(question, schema);
    console.log('Generated SQL Query:', sqlQuery);

    const results = await runSQLQuery(sqlQuery);
    console.log('Query Results:', results);
  } catch (err) {
    console.error('Error:', err);
  }
};

main();
