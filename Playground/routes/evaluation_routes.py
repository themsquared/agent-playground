"""
Routes for evaluation-related endpoints.
"""
from flask import Blueprint, jsonify, request
from uuid import uuid4
from datetime import datetime
import psycopg2
from psycopg2.extras import Json
import os
from dotenv import load_dotenv
from ..state import providers

evaluation_bp = Blueprint('evaluation', __name__, url_prefix='/api/evaluation')

# Load database configuration from environment variables
load_dotenv()
DB_CONNECTION = os.getenv('DATABASE_URL')

def get_db_connection():
    """Get a database connection"""
    return psycopg2.connect(DB_CONNECTION)

# Create tables if they don't exist
def init_db():
    """Initialize database tables"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Create evaluation_tests table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS evaluation_tests (
                    id UUID PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    questions TEXT[] NOT NULL,
                    total_cost DECIMAL(10, 6) NOT NULL DEFAULT 0
                )
            """)
            
            # Create evaluation_results table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS evaluation_results (
                    id UUID PRIMARY KEY,
                    test_id UUID REFERENCES evaluation_tests(id),
                    provider VARCHAR(50) NOT NULL,
                    model_id VARCHAR(100) NOT NULL,
                    question_index INTEGER NOT NULL,
                    response TEXT NOT NULL,
                    rank INTEGER,
                    cost DECIMAL(10, 6) NOT NULL DEFAULT 0,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

# Initialize database on module load
init_db()

@evaluation_bp.post('/evaluate')
async def evaluate_models():
    """Evaluate models with given questions"""
    data = request.json
    test_id = data.get('id')
    name = data.get('name')
    questions = data.get('questions', [])
    selected_models = data.get('models', [])

    print(f"Received evaluation request: {data}")

    if not questions:
        return jsonify({'error': 'No questions provided'}), 400

    if not name:
        return jsonify({'error': 'Test name is required'}), 400

    if not selected_models:
        return jsonify({'error': 'No models selected'}), 400

    try:
        results = []
        total_cost = 0

        # Get responses from selected providers and models
        for model_info in selected_models:
            provider_name = model_info.get('provider')
            model_id = model_info.get('modelId')

            print(f"Processing model: {provider_name}/{model_id}")

            if not provider_name or not model_id:
                print(f"Invalid model info: {model_info}")
                continue

            if provider_name not in providers:
                print(f"Provider {provider_name} not found")
                continue

            provider = providers[provider_name]
            if not provider.client:
                await provider.initialize()

            # Set the model for the provider
            provider.model = model_id
            print(f"Evaluating with {provider_name}/{model_id}")

            for i, question in enumerate(questions):
                try:
                    response = await provider.generate(
                        prompt=question,
                        temperature=0.7
                    )

                    result = {
                        'provider': provider_name,
                        'modelId': model_id,
                        'questionIndex': i,
                        'response': response.content,
                        'cost': response.cost['total_cost'],
                        'rank': None  # Initialize rank as null
                    }
                    print(f"Got response for {provider_name}/{model_id}: {result}")
                    results.append(result)
                    total_cost += response.cost['total_cost']
                except Exception as e:
                    print(f"Error getting response from {provider_name}/{model_id}: {e}")
                    continue

        if not results:
            return jsonify({'error': 'No responses received from any model'}), 500

        response_data = {
            'id': test_id,
            'name': name,
            'created_at': datetime.utcnow().isoformat(),
            'questions': questions,
            'total_cost': total_cost,
            'results': results
        }
        print(f"Sending evaluation response: {response_data}")
        return jsonify(response_data)

    except Exception as e:
        print(f"Error during evaluation: {e}")
        return jsonify({'error': str(e)}), 500

@evaluation_bp.post('/save')
async def save_evaluation():
    """Save evaluation results"""
    data = request.json
    test_id = str(uuid4())
    
    print("Saving evaluation data:", data)  # Debug log
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Save test information
                cur.execute(
                    """
                    INSERT INTO evaluation_tests (id, name, questions, total_cost)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    """,
                    (test_id, data['name'], data['questions'], data['total_cost'])
                )

                # Save individual results
                for result in data['results']:
                    result_id = str(uuid4())
                    print(f"Saving result: {result}")  # Debug log
                    cur.execute(
                        """
                        INSERT INTO evaluation_results 
                        (id, test_id, provider, model_id, question_index, response, rank, cost)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            result_id,
                            test_id,
                            result['provider'],
                            result.get('modelId', ''),  # Use get() with default value
                            result['questionIndex'],
                            result['response'],
                            result.get('rank'),  # Use get() for optional fields
                            result.get('cost', 0)  # Use get() with default value
                        )
                    )
                
                conn.commit()
                
        return jsonify({
            'message': 'Evaluation saved successfully',
            'test_id': test_id
        })
    except Exception as e:
        print(f"Error saving evaluation: {e}")  # Debug log
        return jsonify({'error': str(e)}), 500

@evaluation_bp.get('/results')
async def get_evaluation_results():
    """Get all evaluation results"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        t.id,
                        t.name,
                        t.created_at,
                        t.questions,
                        t.total_cost,
                        json_agg(json_build_object(
                            'id', r.id,
                            'provider', r.provider,
                            'modelId', r.model_id,
                            'questionIndex', r.question_index,
                            'response', r.response,
                            'rank', r.rank,
                            'cost', r.cost
                        )) as results
                    FROM evaluation_tests t
                    LEFT JOIN evaluation_results r ON t.id = r.test_id
                    GROUP BY t.id, t.name, t.created_at, t.questions, t.total_cost
                    ORDER BY t.created_at DESC
                """)
                
                results = []
                for row in cur.fetchall():
                    # Ensure results is not null (can happen with LEFT JOIN)
                    result_data = row[5] if row[5] and row[5][0] is not None else []
                    
                    # Map the results to ensure consistent property names
                    mapped_results = []
                    for r in result_data:
                        mapped_results.append({
                            'id': r.get('id'),
                            'provider': r.get('provider'),
                            'modelId': r.get('modelId'),
                            'questionIndex': r.get('questionIndex'),
                            'response': r.get('response'),
                            'rank': r.get('rank'),
                            'cost': float(r.get('cost', 0))
                        })
                    
                    results.append({
                        'id': row[0],
                        'name': row[1],
                        'created_at': row[2].isoformat(),
                        'questions': row[3],
                        'total_cost': float(row[4]),
                        'results': mapped_results
                    })
                
                print("Fetched evaluation results:", results)  # Debug log
                return jsonify(results)
    except Exception as e:
        print(f"Error fetching evaluation results: {e}")  # Debug log
        return jsonify({'error': str(e)}), 500

@evaluation_bp.get('/csv/<test_id>')
async def get_evaluation_csv(test_id):
    """Get evaluation results as CSV"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        t.name as test_name,
                        t.questions[r.question_index + 1] as question,
                        r.provider,
                        r.model_id,
                        r.response,
                        r.rank,
                        r.cost
                    FROM evaluation_tests t
                    JOIN evaluation_results r ON t.id = r.test_id
                    WHERE t.id = %s
                    ORDER BY r.question_index, r.rank
                """, (test_id,))
                
                # Generate CSV content
                import csv
                from io import StringIO
                
                output = StringIO()
                writer = csv.writer(output)
                writer.writerow(['Test Name', 'Question', 'Provider', 'Model', 'Response', 'Rank', 'Cost'])
                
                for row in cur.fetchall():
                    writer.writerow(row)
                
                from flask import Response
                return Response(
                    output.getvalue(),
                    mimetype='text/csv',
                    headers={'Content-Disposition': f'attachment; filename=evaluation_{test_id}.csv'}
                )
    except Exception as e:
        return jsonify({'error': str(e)}), 500 