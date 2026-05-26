/**
 * Node.js Integration Example
 * 
 * This demonstrates how to integrate the workflow automation system
 * with Node.js applications using REST API calls.
 * 
 * Installation:
 * npm install axios dotenv
 */

const axios = require('axios');
require('dotenv').config();

// Configure API client
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:5000/api';

class WorkflowAutomationClient {
    constructor(baseURL = API_BASE_URL) {
        this.client = axios.create({
            baseURL: baseURL,
            timeout: 10000,
            headers: {
                'Content-Type': 'application/json',
                'X-User-ID': process.env.USER_ID || 'nodejs-client'
            }
        });
    }

    /**
     * Execute a workflow
     */
    async executeWorkflow(workflowId, data) {
        try {
            const response = await this.client.post(
                `/workflows/${workflowId}/execute`,
                data
            );
            return response.data;
        } catch (error) {
            throw new Error(`Failed to execute workflow: ${error.message}`);
        }
    }

    /**
     * Get workflow execution status
     */
    async getExecutionStatus(executionId) {
        try {
            const response = await this.client.get(
                `/executions/${executionId}`
            );
            return response.data;
        } catch (error) {
            throw new Error(`Failed to get execution status: ${error.message}`);
        }
    }

    /**
     * Get execution logs
     */
    async getExecutionLogs(executionId) {
        try {
            const response = await this.client.get(
                `/executions/${executionId}/logs`
            );
            return response.data;
        } catch (error) {
            throw new Error(`Failed to get execution logs: ${error.message}`);
        }
    }

    /**
     * Submit a form
     */
    async submitForm(formId, formData) {
        try {
            const response = await this.client.post(
                `/forms/${formId}/submit`,
                formData
            );
            return response.data;
        } catch (error) {
            throw new Error(`Failed to submit form: ${error.message}`);
        }
    }

    /**
     * Get form submission details
     */
    async getSubmission(submissionId) {
        try {
            const response = await this.client.get(
                `/submissions/${submissionId}`
            );
            return response.data;
        } catch (error) {
            throw new Error(`Failed to get submission: ${error.message}`);
        }
    }

    /**
     * Export submission as JSON
     */
    async exportSubmission(submissionId) {
        try {
            const response = await this.client.get(
                `/submissions/${submissionId}/export`
            );
            return response.data;
        } catch (error) {
            throw new Error(`Failed to export submission: ${error.message}`);
        }
    }

    /**
     * Upload a document
     */
    async uploadDocument(filePath, ownderId, metadata = {}) {
        try {
            const FormData = require('form-data');
            const fs = require('fs');
            const form = new FormData();

            form.append('file', fs.createReadStream(filePath));
            form.append('owner_id', ownderId);
            form.append('metadata', JSON.stringify(metadata));

            const response = await this.client.post(
                '/documents/upload',
                form,
                { headers: form.getHeaders() }
            );
            return response.data;
        } catch (error) {
            throw new Error(`Failed to upload document: ${error.message}`);
        }
    }

    /**
     * Get document details
     */
    async getDocument(documentId) {
        try {
            const response = await this.client.get(
                `/documents/${documentId}`
            );
            return response.data;
        } catch (error) {
            throw new Error(`Failed to get document: ${error.message}`);
        }
    }

    /**
     * Search documents
     */
    async searchDocuments(query = null, tags = []) {
        try {
            const params = {};
            if (query) params.q = query;
            if (tags.length > 0) params.tags = tags;

            const response = await this.client.get(
                '/documents/search',
                { params }
            );
            return response.data;
        } catch (error) {
            throw new Error(`Failed to search documents: ${error.message}`);
        }
    }

    /**
     * Send email notification
     */
    async sendEmail(recipient, subject, options = {}) {
        try {
            const response = await this.client.post(
                '/notifications/send-email',
                {
                    recipient,
                    subject,
                    body: options.body,
                    template_name: options.templateName,
                    template_data: options.templateData
                }
            );
            return response.data;
        } catch (error) {
            throw new Error(`Failed to send email: ${error.message}`);
        }
    }

    /**
     * Get notification status
     */
    async getNotification(notificationId) {
        try {
            const response = await this.client.get(
                `/notifications/${notificationId}`
            );
            return response.data;
        } catch (error) {
            throw new Error(`Failed to get notification: ${error.message}`);
        }
    }
}

// Example usage
async function example() {
    const client = new WorkflowAutomationClient();

    try {
        console.log('🚀 Leceil Morgan Corp - Node.js Integration Example\n');

        // Example 1: Submit a form and execute workflow
        console.log('1️⃣ Submitting Employee Onboarding Form...');
        const formData = {
            full_name: 'Jane Doe',
            email: 'jane.doe@leceilmorgan.com',
            department: 'IT',
            position: 'DevOps Engineer',
            start_date: '2026-06-15'
        };

        const submission = await client.submitForm('emp_onboarding', formData);
        console.log(`✅ Form submitted: ${submission.submission_id}\n`);

        // Example 2: Execute workflow
        console.log('2️⃣ Executing Approval Workflow...');
        const execution = await client.executeWorkflow('approval_workflow', {
            document_name: 'Employee Contract.pdf',
            requester: 'hr@leceilmorgan.com'
        });
        console.log(`✅ Workflow execution started: ${execution.execution_id}\n`);

        // Example 3: Check execution status
        console.log('3️⃣ Checking Workflow Status...');
        const status = await client.getExecutionStatus(execution.execution_id);
        console.log(`✅ Execution status: ${status.status}`);
        console.log(`   Logs: ${status.logs.length} entries\n`);

        // Example 4: Search documents
        console.log('4️⃣ Searching Documents...');
        const documents = await client.searchDocuments(null, ['policies', 'hr']);
        console.log(`✅ Found ${documents.count} document(s)\n`);

        // Example 5: Send email notification
        console.log('5️⃣ Sending Email Notification...');
        const notification = await client.sendEmail(
            'manager@leceilmorgan.com',
            'New Employee Onboarding',
            {
                body: 'Please review the new employee onboarding form.',
                templateName: 'approval_request',
                templateData: {
                    employee_name: 'Jane Doe',
                    department: 'IT'
                }
            }
        );
        console.log(`✅ Notification sent: ${notification.notification_id}\n`);

        console.log('✨ All examples completed successfully!');

    } catch (error) {
        console.error(`❌ Error: ${error.message}`);
    }
}

// Export for use in other modules
module.exports = WorkflowAutomationClient;

// Run example if this is the main module
if (require.main === module) {
    example();
}
