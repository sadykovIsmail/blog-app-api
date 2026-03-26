'use client';

import { useState } from 'react';
import { formatDistanceToNow } from 'date-fns';
import { MessageCircle, Reply, Trash2 } from 'lucide-react';
import { Comment } from '@/lib/types';
import { useAuth } from '@/contexts/AuthContext';
import { commentsApi } from '@/lib/api';
import toast from 'react-hot-toast';

interface Props {
  comments: Comment[];
  onAddComment: (content: string, parentId?: number) => Promise<void>;
  onDeleteComment?: (id: number) => void;
}

function CommentItem({
  comment,
  onReply,
  onDelete,
  currentUsername,
}: {
  comment: Comment;
  onReply: (parentId: number) => void;
  onDelete: (id: number) => void;
  currentUsername?: string;
}) {
  return (
    <div className="space-y-3">
      <div className="rounded-xl bg-gray-50 p-4">
        <div className="mb-2 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-600">
              {comment.username[0].toUpperCase()}
            </div>
            <span className="text-sm font-medium">{comment.username}</span>
            <span className="text-xs text-gray-400">
              {formatDistanceToNow(new Date(comment.created_at), { addSuffix: true })}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => onReply(comment.id)}
              className="flex items-center gap-1 text-xs text-gray-400 hover:text-blue-500"
            >
              <Reply className="h-3.5 w-3.5" /> Reply
            </button>
            {currentUsername === comment.username && (
              <button
                onClick={() => onDelete(comment.id)}
                className="flex items-center gap-1 text-xs text-gray-400 hover:text-red-500"
              >
                <Trash2 className="h-3.5 w-3.5" />
              </button>
            )}
          </div>
        </div>
        <p className="text-sm text-gray-700">{comment.content}</p>
      </div>

      {comment.replies.length > 0 && (
        <div className="ml-6 space-y-3 border-l-2 border-gray-100 pl-4">
          {comment.replies.map((reply) => (
            <CommentItem
              key={reply.id}
              comment={reply}
              onReply={onReply}
              onDelete={onDelete}
              currentUsername={currentUsername}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default function CommentSection({ comments: initialComments, onAddComment, onDeleteComment }: Props) {
  const { user, isAuthenticated } = useAuth();
  const [comments, setComments] = useState(initialComments);
  const [content, setContent] = useState('');
  const [replyTo, setReplyTo] = useState<number | undefined>();
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) return;
    setSubmitting(true);
    try {
      await onAddComment(content, replyTo);
      setContent('');
      setReplyTo(undefined);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await commentsApi.delete(id);
      setComments((prev) => prev.filter((c) => c.id !== id));
      onDeleteComment?.(id);
      toast.success('Comment deleted');
    } catch {
      toast.error('Failed to delete comment');
    }
  };

  return (
    <section id="comments" className="mt-10">
      <h3 className="mb-6 flex items-center gap-2 text-xl font-bold">
        <MessageCircle className="h-5 w-5 text-blue-600" />
        Comments ({comments.length})
      </h3>

      {isAuthenticated && (
        <form onSubmit={handleSubmit} className="mb-8 space-y-3">
          {replyTo && (
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <Reply className="h-4 w-4" />
              Replying to a comment
              <button
                type="button"
                onClick={() => setReplyTo(undefined)}
                className="ml-2 text-red-400 hover:text-red-600"
              >
                Cancel
              </button>
            </div>
          )}
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Share your thoughts..."
            rows={3}
            maxLength={1000}
            className="w-full rounded-xl border border-gray-200 p-3 text-sm focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
          />
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-400">{content.length}/1000</span>
            <button
              type="submit"
              disabled={submitting || !content.trim()}
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {submitting ? 'Posting...' : 'Post Comment'}
            </button>
          </div>
        </form>
      )}

      {!isAuthenticated && (
        <p className="mb-6 rounded-xl bg-gray-50 p-4 text-sm text-gray-500">
          <a href="/login" className="text-blue-600 hover:underline">Sign in</a> to leave a comment.
        </p>
      )}

      <div className="space-y-4">
        {comments.map((comment) => (
          <CommentItem
            key={comment.id}
            comment={comment}
            onReply={setReplyTo}
            onDelete={handleDelete}
            currentUsername={user?.username}
          />
        ))}
        {comments.length === 0 && (
          <p className="py-8 text-center text-sm text-gray-400">No comments yet. Be the first!</p>
        )}
      </div>
    </section>
  );
}
