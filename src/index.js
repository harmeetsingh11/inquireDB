const sqlite3 = require('sqlite3').verbose();
const readline = require('readline');
const { config } = require('dotenv');
const Groq = require('groq-sdk').default;
const path = require('path');

// Load environment variables from .env file
config();

// Initialize Groq SDK
const groq = new Groq({ apiKey: process.env.GROQ_API_KEY });

// Define the path to the database file
const dbPath = path.join(__dirname, '../Databases/northwind.db');

// Initialize SQLite database
const db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.error('Error opening database:', err.message);
  } else {
    console.log('Connected to the SQLite database.');
  }
});

// Function to fetch table and column names from the database
const getDatabaseSchema = () => {
  return new Promise((resolve, reject) => {
    db.all(
      `SELECT name FROM sqlite_master WHERE type='table';`,
      (err, tables) => {
        if (err) {
          reject(err);
          return;
        }

        const schema = {};
        let pending = tables.length;

        if (pending === 0) {
          resolve(schema);
          return;
        }

        tables.forEach((table) => {
          db.all(`PRAGMA table_info(${table.name});`, (err, columns) => {
            if (err) {
              reject(err);
              return;
            }

            schema[table.name] = columns.map((column) => column.name);
            pending -= 1;

            if (pending === 0) {
              resolve(schema);
            }
          });
        });
      }
    );
  });
};

// Function to get a SQL query from LLM using Groq
const getSQLQueryFromLLM = async (question, schema) => {
  try {
    const schemaDescription = Object.entries(schema)
      .map(
        ([table, columns]) =>
          `Table ${table} with columns: ${columns.join(', ')}`
      )
      .join('\n');

    const response = await groq.chat.completions.create({
      messages: [
        {
          role: 'user',
          content: `Here is the database schema:\n${schemaDescription}\nConvert the following natural language question to an SQL query: "${question}"`,
        },
      ],
      model: 'llama3-8b-8192',
    });
    const generatedQuery = response.choices[0]?.message?.content.trim();
    if (!generatedQuery) {
      throw new Error('The LLM did not return a valid SQL query.');
    }
    return generatedQuery;
  } catch (error) {
    console.error('Error fetching SQL query from LLM:', error);
    throw new Error('Failed to get SQL query from LLM');
  }
};

// Function to run a SQL query and return the results
const runSQLQuery = (query) => {
  return new Promise((resolve, reject) => {
    db.all(query, [], (err, rows) => {
      if (err) {
        reject(err.message);
      } else {
        resolve(rows);
      }
    });
  });
};

// Function to handle user input and provide answers
const handleUserInput = async (input) => {
  try {
    const schema = await getDatabaseSchema();
    const sqlQuery = await getSQLQueryFromLLM(input, schema);
    console.log('Generated SQL Query:', sqlQuery); // Log the generated SQL query for debugging

    const results = await runSQLQuery(sqlQuery);
    if (results.length === 0) {
      console.log('No data found');
    } else {
      console.log('Query Results:', results);
    }
  } catch (error) {
    console.error('Error:', error.message);
  }
};

// Setup readline interface for command-line interaction
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  prompt: 'Ask your question: ',
});

rl.prompt();

rl.on('line', (line) => {
  handleUserInput(line.trim());
  rl.prompt();
}).on('close', () => {
  console.log('Exiting the application. Goodbye!');
  db.close();
});
