-- 长按 Shift 临时英文处理器
-- 设计原则：完全不调用 set_option("ascii_mode")，避免触发 notifier 循环
-- 行为：
--   1. 有编码时按下 Shift：不拦截，让 ascii_composer 执行 commit_code（短按流程不变）
--   2. 无编码时按下 Shift：进入 hold_shift 状态，不切换 ascii_mode
--      - 按住期间字母键直接 push_input 小写字母到 context（中文模式下 speller 会把它当 ascii 处理）
--      - 松开时若为短按（没按过其他键），则切换一次中英文
--      - 松开时若为长按，不切换（保持原模式）

local XK_Shift_L = 0xffe1
local XK_Shift_R = 0xffe2
local rime = require "sbxlm.lib"

local this = {}

function this.init(env)
  env.hold_shift = false
  env.had_other_key = false
  env.was_english_on_press = false
end

---@param key_event KeyEvent
---@param env Env
function this.func(key_event, env)
  local context = env.engine.context
  local keycode = key_event.keycode

  -- 长按 Shift 临时英文模式期间，字母键转小写直接上屏
  if env.hold_shift and not key_event:release()
     and not key_event:alt() and not key_event:ctrl() and not key_event:super() then
    -- A-Z（带 Shift 修饰符）→ 转小写直接 commit_text 上屏
    if keycode >= 0x41 and keycode <= 0x5a then
      env.had_other_key = true
      local ch = string.char(keycode + 32)
      env.engine:commit_text(ch)
      return rime.process_results.kAccepted
    end
  end

  -- 非 Shift 键：记录其他按键
  if keycode ~= XK_Shift_L and keycode ~= XK_Shift_R then
    if env.hold_shift and not key_event:release() then
      env.had_other_key = true
    end
    return rime.process_results.kNoop
  end

  -- Shift 松开事件
  if key_event:release() then
    if env.hold_shift then
      local was_short = not env.had_other_key
      env.hold_shift = false
      env.had_other_key = false
      if was_short then
        -- 短按：切换一次中英文
        context:set_option("ascii_mode", not env.was_english_on_press)
      end
      -- 长按：不切换，保持原模式（因为期间没有 set_option）
      env.was_english_on_press = false
      return rime.process_results.kAccepted
    end
    return rime.process_results.kNoop
  end

  -- Shift 按下事件
  -- 有编码：不拦截，让 ascii_composer 执行 commit_code
  if context:is_composing() then
    return rime.process_results.kNoop
  end

  -- 无编码：进入 hold_shift 状态，不切换 ascii_mode
  env.hold_shift = true
  env.had_other_key = false
  env.was_english_on_press = context:get_option("ascii_mode")
  return rime.process_results.kAccepted
end

return this
